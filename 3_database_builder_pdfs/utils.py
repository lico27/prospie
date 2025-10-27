import re
import ocrmypdf

def check_accounts(accounts_content):

    #check text is not unexpectedly short
    if len(accounts_content) < 100:
        return False
    
    #check proportion of unusual characters is not too high
    non_ascii = sum(1 for char in accounts_content if ord(char) > 127)
    if non_ascii / len(accounts_content) > 0.3:
        return False
    
    #check years are present and from 2000 onwards
    year_pattern = r"\b20\d{2}\b"
    if not re.search(year_pattern, accounts_content):
        return False
    
    return True

def ocr_accounts(pdf_path):
    """
    Runs OCR on downloaded accounts files to extract text into a format that can be read and analysed. 
    Resaves accounts files once text is extracted/converted.
    """
    try:
        ocrmypdf.ocr(
            pdf_path,
            pdf_path,
            skip_text=True,
            force_ocr=False,
            optimize=1,
            language="eng",
            progress_bar=False,
            invalidate_digital_signatures=True
        )
        return True
    except ocrmypdf.exceptions.PriorOcrFoundError:
        #skip if ocr not needed
        print(f"OCR not required: {pdf_path}")
        return True
    except Exception as e:
        print(f"Error processing {pdf_path}: {e}")
        return False
    
def extract_after_para(para_pattern, text):
    """
    Extracts content from text after a given paragraph reference.
    Checks for empty cells in CC17a form.
    """
    match = re.search(para_pattern, text, re.IGNORECASE)
    if not match:
        return None

    start = match.end()

    #check for empty cell
    next_content = text[start:start+100].strip()
    if next_content.startswith("Para ") or re.match(r"^[A-Z]*\d+[A-Z]*\s*$", next_content.split("\n")[0]):
        return None

    next_para = re.search(r"\nPara\s+\d+\.\d+", text[start:])
    
    if next_para:
        #estimate end of content
        tentative_end = start + next_para.start()
        chunk_before_para = text[max(start, tentative_end - 400):tentative_end]
        
        #use common patterns used in following sections
        desc_pattern = r"\n(Summary of|Policy on|Contribution made|Additional|Whether|Other)[^\n]*$"
        desc_match = re.search(desc_pattern, chunk_before_para, re.IGNORECASE)
        
        if desc_match:
            #use actual end if content found otherwise use estimate
            actual_end = max(start, tentative_end - 400) + desc_match.start()
            content = text[start:actual_end]
        else:
            content = text[start:tentative_end]
    else:
        #try and find heading if not found
        section_match = re.search(r"\n\n[A-Z][a-zA-Z\s]+\n", text[start:start+2000])
        if section_match:
            content = text[start:start + section_match.start()]
        else:
            #use reasonable estimate of length
            content = text[start:start + 1500]
    
    content = content.strip()
    return content if len(content) >= 20 else None

def find_next_section(text, start_pos):
        """
        Finds the next major section heading.
        """
        #pattern for multi-word headings or known single-word sections
        section_pattern = r'\n\n\s*([A-Z][A-Za-z]+(?:\s+[A-Za-z]+)+|Financial|Structure|Governance|Risk|Plans|Funding|Reserves)\s*\n'
        
        match = re.search(section_pattern, text[start_pos:])
        if match:
            return start_pos + match.start()
        
        return None