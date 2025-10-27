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
    year_pattern = r'\b20\d{2}\b'
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