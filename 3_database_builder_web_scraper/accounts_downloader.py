from bs4 import BeautifulSoup
import requests
import pandas as pd
import time
import os

def get_accounts_urls(c_nums):
    
    accounts_data = []
    inaccessible_accounts = []
       
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

            #check if no accounts links found
            if not accounts_links:
                inaccessible_accounts.append({"registered_num": num,
                                              "year_end": None,
                                              "url": None,
                                              "accounts_accessed": False})
                continue

            #limit requests
            time.sleep(1.0)

        except Exception as e:
            print(f"Error fetching or parsing accounts page for {num}: {e}")
            inaccessible_accounts.append({"registered_num": num,
                                          "year_end": None,
                                          "url": None,
                                          "accounts_accessed": False})
            continue

        for link in accounts_links:
            try:
                #get full url of accounts
                pdf_url = link.get("href")
                if not pdf_url:
                    continue

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
                    "url": pdf_url,
                    "accounts_accessed": True
                })

                #limit requests
                time.sleep(0.5)

            except Exception as e:
                print(f"Error getting accounts URL for {num}: {e}")
                continue

    #convert/merge lists as dataframe
    try:
        if not accounts_data or len(accounts_data) == 0:
            accounts = pd.DataFrame(columns=["registered_num", "year_end", "url"])
        else:
            accounts = pd.DataFrame(accounts_data)
    except Exception as e:
        print(f"Error creating DataFrame: {e}")
        raise

    try:
        if not inaccessible_accounts or len(inaccessible_accounts) == 0:
            inaccessible = pd.DataFrame(columns=["registered_num", "year_end", "url", "accounts_accessed"])
        else:
            inaccessible = pd.DataFrame(inaccessible_accounts)
    except Exception as e:
        print(f"Error creating DataFrame: {e}")
        raise   
    
    accounts = pd.concat([accounts, inaccessible], ignore_index=True)

    return accounts

def download_accounts(url, path):
    
    if url is not None:

        #only download if file doesn't already exist
        if os.path.exists(path):
            print(f"File already exists, skipping: {path}")
            return True
        
        #create directory if it doesn't exist
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        #download with headers
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        #write binary content to file
        with open(path, "wb") as f:
            f.write(response.content)
        
        return True
    return False

