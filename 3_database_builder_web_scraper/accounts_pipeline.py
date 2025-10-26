import pandas as pd
import ocrmypdf
from accounts_downloader import get_accounts_urls, download_accounts

def get_accounts(c_nums):
    accounts = get_accounts_urls(c_nums)
    return accounts

def save_accounts(accounts):
    for i, row in accounts.iterrows():
        accounts_url = row["url"]
        registered_num = row["registered_num"]
        year = row["year_end"]

        #only download if url exists
        if accounts_url is not None:
            try:
                #download accounts
                save_path = f"accounts/{registered_num}_{year}.pdf"
                success = download_accounts(accounts_url, save_path)

                #add to df if successful
                if success:
                    accounts.at[i, "file_path"] = save_path
            except Exception as e:
                accounts.at[i, "file_path"] = None
        else:
            #no url available
            accounts.at[i, "file_path"] = None

    return accounts

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