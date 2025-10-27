import pdfplumber
import fitz
from utils import check_accounts

def get_accounts_text(pdf_path, accounts_df, index):
    """ 
    Extracts text from an accounts file and saves it to the dataframe.
    Uses a two-step process to deal with accounts containing CID characters.
    """
    try:
        #try fitz for speed
        text = ""
        doc = fitz.open(pdf_path)
        for page in doc:
            text += page.get_text() + "\n"
        doc.close()
        
        #check for validity of text
        if text and "(cid:" not in text[:1000] and check_accounts(text):
            accounts_df.at[index, "accounts_text"] = text
            return
        
        #backup attempt for more complex files
        text = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        
        #validate again before saving
        if check_accounts(text):
            accounts_df.at[index, "accounts_text"] = text
        else:
            print(f"Text failed validation for {pdf_path}")
            accounts_df.at[index, "accounts_text"] = None
        
    except Exception as e:
        print(f"Error extracting text from {pdf_path}: {e}")
        accounts_df.at[index, "accounts_text"] = None