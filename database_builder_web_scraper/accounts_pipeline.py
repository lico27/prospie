from bs4 import BeautifulSoup
import requests
import PyPDF2
from io import BytesIO
import pandas as pd
import time

def get_accounts_data(c_nums):
    
    accounts_data = []

    for num in c_nums:
        try:
            #get charity's accounts page
            headers = {"User-Agent": "Mozilla/5.0"}
            result = requests.get(f"https://register-of-charities.charitycommission.gov.uk/en/charity-search/-/charity-details/{num}/accounts-and-annual-returns?_uk_gov_ccew_onereg_charitydetails_web_portlet_CharityDetailsPortlet_organisationNumber={num}", headers=headers)
            result.raise_for_status()

            #parse page and find links to download accounts
            src = result.content
            soup = BeautifulSoup(src, "lxml")
            accounts_links = soup.find_all("a", class_="accounts-download-link")

            #limit requests
            time.sleep(1.0)

        except Exception as e:
            print(f"Error fetching or parsing accounts page for {num}: {e}")
            continue

        for link in accounts_links:
            try:
                #get full url of accounts
                pdf_url = link["href"]
                
                #get pdf
                pdf_response = requests.get(pdf_url, headers=headers)
                pdf_response.raise_for_status()
                
                #read pdf and extract contents
                pdf_file = BytesIO(pdf_response.content)
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                full_text = ""
                for page in pdf_reader.pages:
                    full_text += page.extract_text()

                #get year end from date
                year_end = None
                aria_label = link.get("aria-label")
                if aria_label:
                    aria_split = aria_label.split()
                    if len(aria_split) >= 2:
                        year = aria_split[-2].rstrip(",.;:")
                        if year.isdigit() and len(year) == 4:
                            year_end = year
                
                #add to list
                accounts_data.append({
                    "registered_num": num,
                    "year_end": year_end,
                    "content": full_text,
                    "url": pdf_url
                })

                # Rate limiting: wait after downloading each PDF
                time.sleep(0.5)

            except Exception as e:
                print(f"Error processing PDF for {num}: {e}")
                continue

    try:
        #convert list to dataframe
        if not accounts_data or len(accounts_data) == 0:
            accounts = pd.DataFrame(columns=["registered_num", "year_end", "content", "url"])
        else:
            accounts = pd.DataFrame(accounts_data)
    except Exception as e:
        print(f"Error creating DataFrame: {e}")
        raise

    return accounts