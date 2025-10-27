import re
from utils import extract_after_para, find_next_section

def find_sections_by_sorp(text):
    """
    Finds required sections by checking if document contains SORP references (i.e. do the accounts use CC17a form).
    """   
    obj_text = None
    achievement_text = None
    has_obj = False
    has_achievement = False
    policy_text = None
    has_policy = False

    #check if objectives/activities sorp references are present
    for para_ref in [r"Para\s+1\.17(?:\s+and\s+1\.19)?", r"Para\s+1\.18", r"Para\s+1\.19"]:
        content = extract_after_para(para_ref, text)
        if content:
            has_obj = True
            if obj_text:
                obj_text += "\n\n" + content
            else:
                obj_text = content
    
    #check if achievements/performance sorp reference is present
    achievement_content = extract_after_para(r"Para\s+1\.20", text)
    if achievement_content:
        has_achievement = True
        achievement_text = achievement_content

    #check if grant policy sorp reference is present
    policy_content = extract_after_para(r"Para\s+1\.38", text)
    if policy_content:
        has_policy = True
        policy_text = policy_content

    #return data found by sorp reference
    return has_obj, obj_text, has_achievement, achievement_text, has_policy, policy_text
    
def find_sections_by_regex(text):
    """
    Finds required sections in documents where SORP references are not present. Matches variable formats of headings using regex.
    """
    #check for combined heading
    combined_pattern = r"""(?i)(?:^|\n)\s*
        (?=.*?(?:object(?:ive)?s?|activit(?:y|ies)))
        (?=.*?(?:achieve(?:ment|ments)?|performances?|results?))
        [^\n]{0,150}?
        (?:public\s+benefit)?
        \s*(?:\n|$)"""

    combined_matches = re.finditer(combined_pattern, text, re.VERBOSE)

    #get section following combined heading
    for combined_match in combined_matches:
        matched_line = combined_match.group().strip()
        if len(matched_line) > 80:
            continue

        sentence_indicators = r'\b(has|have|will|established|provides?|makes?|gives?|the\s+\w+\s+(is|are|has|have))\b'
        if re.search(sentence_indicators, matched_line, re.IGNORECASE):
            continue
        
        start_pos = combined_match.end()
        end_pos = find_next_section(text, start_pos)
        
        if end_pos:
            combined_text = text[start_pos:end_pos]
        else:
            combined_text = text[start_pos:start_pos + 2000]
        
        combined_text = combined_text.strip()

        if len(combined_text) >= 20:
            return True, combined_text, True, combined_text, False, None
        else:
            return True, None, True, None, False, None

    #check for separate headings
    obj_act_pattern = r"""(?i)(?:^|\n)\s*(?:
        (?:object(?:ive)?s?)|
        (?:activit(?:y|ies))|
        (?:(?:object(?:ive)?s?)[\s\&\-]*(?:and|&)[\s\&\-]*(?:activit(?:y|ies)))|
        (?:(?:activit(?:y|ies))[\s\&\-]*(?:and|&)[\s\&\-]*(?:object(?:ive)?s?))
    )(?:.{0,40}?public\s+benefit)?\s*(?:\n|$)"""

    ach_perf_pattern = r"""(?i)(?:^|\n)\s*(?:
        (?:achieve(?:ment|ments)?)|
        (?:performances?)|
        (?:results?)
    )(?:\s*(?:and|&|\/|,)?\s*(?:achieve(?:ment|ments)?|performances?|results?))*\s*(?:\n|$)"""

    pol_pattern = r"""(?i)(?:^|\n)\s*(?:
        polic(?:y|ies)\s+(?:for|on)\s+(?:grants?|donations?)(?:[\s\-]+(?:giving|making))?
        |
        (?:grants?|donations?)(?:[\s\-]+(?:giving|making))?\s+polic(?:y|ies)
        |
        strateg(?:y|ies)\s+(?:for|on)\s+(?:grants?|donations?)(?:[\s\-]+(?:giving|making))?
        |
        (?:grants?|donations?)(?:[\s\-]+(?:giving|making))?\s+strateg(?:y|ies)
    )\s*(?:\n|$)"""

    has_obj = False
    obj_text = None
    has_achievement = False
    achievement_text = None
    has_policy = False
    policy_text = None

    #get objectives/activities section
    obj_match = re.search(obj_act_pattern, text, re.VERBOSE)
    if obj_match:
        has_obj = True
        start_pos = obj_match.end()
        end_pos = find_next_section(text, start_pos)
        
        if end_pos:
            obj_text = text[start_pos:end_pos]
        else:
            obj_text = text[start_pos:start_pos + 2000]
        
        obj_text = obj_text.strip()
        if len(obj_text) < 20:
            obj_text = None

    #get achievements/performance section
    achievement_match = re.search(ach_perf_pattern, text, re.VERBOSE)
    if achievement_match:
        has_achievement = True
        start_pos = achievement_match.end()
        end_pos = find_next_section(text, start_pos)
        
        if end_pos:
            achievement_text = text[start_pos:end_pos]
        else:
            achievement_text = text[start_pos:start_pos + 2000]

        achievement_text = achievement_text.strip()
        if len(achievement_text) < 20:
            achievement_text = None

    #get grant policy section
    policy_match = re.search(pol_pattern, text, re.VERBOSE)
    if policy_match:
        has_policy = True
        start_pos = policy_match.end()
        end_pos = find_next_section(text, start_pos)

        if end_pos:
            policy_text = text[start_pos:end_pos]
        else:
            policy_text = text[start_pos:start_pos + 2000]

        policy_text = policy_text.strip()
        if len(policy_text) < 20:
            policy_text = None

    return has_obj, obj_text, has_achievement, achievement_text, has_policy, policy_text