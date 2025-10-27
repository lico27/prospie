import re
from utils import extract_after_para

def find_sections_by_sorp(text):
    """
    Finds required sections by checking if document contains SORP references (i.e. do the accounts use CC17a form).
    """   
    obj_text = None
    achievement_text = None
    has_obj = False
    has_achievement = False

    #check if objectives/activities sorp references are present
    for para_ref in [r'Para\s+1\.17(?:\s+and\s+1\.19)?', r'Para\s+1\.18', r'Para\s+1\.19']:
        content = extract_after_para(para_ref, text)
        if content:
            has_obj = True
            if obj_text:
                obj_text += "\n\n" + content
            else:
                obj_text = content
    
    #check if achievements/performance sorp reference is present
    achievement_content = extract_after_para(r'Para\s+1\.20', text)
    if achievement_content:
        has_achievement = True
        achievement_text = achievement_content
    
    #return data found by sorp reference
    if has_obj or has_achievement:
        return has_obj, obj_text, has_achievement, achievement_text
    else:
        return False, None, False, None
    
def find_sections_by_regex(text):

    
    return has_obj, obj_text, has_achievement, achievement_text
