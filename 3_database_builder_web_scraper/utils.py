import re

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