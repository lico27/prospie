from logic_utils import get_name_from_id, get_id_from_name, get_granularity_weight, check_if_parent, calculate_similarity_score
import pandas as pd
import json
from datetime import datetime

def check_existing_relationship(grants_df, funder_num, user_num):
    """
    Checks if funder has ever given a grant to the user.
    """
    relationship = grants_df[
        (grants_df["funder_num"] == funder_num) &
        (grants_df["recipient_id"] == user_num)
    ]

    num_grants = len(relationship)
    existing_relationship = num_grants > 0

    return existing_relationship, num_grants, relationship

def check_areas(funder_list, user_list, areas_df, hierarchies_df):
    """
    Calculates a score based on matches between the funder's and user's stated areas.
    """

    #convert names to ids
    funder_ids = [get_id_from_name(name, areas_df) for name in funder_list if get_id_from_name(name, areas_df) is not None]
    user_ids = [get_id_from_name(name, areas_df) for name in user_list if get_id_from_name(name, areas_df) is not None]
    
    #avoid zero division
    if len(user_ids) == 0:
        return 0.0, []
    
    #store ids as set and scores/reasoning as lists
    funder_set = set(funder_ids)
    scores = []
    reasoning = []
    
    for user_area in user_ids:
        user_area_name = get_name_from_id(user_area, areas_df)
        
        #check for exact match
        if user_area in funder_set:
            score = get_granularity_weight(user_area, areas_df) * 1.0
            scores.append(score)
            reasoning.append(f"Exact match: {user_area_name}")
        
        #check if user area is within funder area
        else:
            hierarchy_user_in_funder = None
            for funder_area in funder_ids:
                if check_if_parent(funder_area, user_area, hierarchies_df):
                    hierarchy_user_in_funder = funder_area
                    break
            
            if hierarchy_user_in_funder:
                parent_name = get_name_from_id(hierarchy_user_in_funder, areas_df)
                score = get_granularity_weight(hierarchy_user_in_funder, areas_df) * 0.6
                scores.append(score)
                reasoning.append(f"Hierarchical match: {user_area_name} (user) within {parent_name} (funder)")
            
            #check if funder area is within user area
            else:
                hierarchy_funder_in_user = None
                for funder_area in funder_ids:
                    if check_if_parent(user_area, funder_area, hierarchies_df):
                        hierarchy_funder_in_user = funder_area
                        break
                
                if hierarchy_funder_in_user:
                    child_name = get_name_from_id(hierarchy_funder_in_user, areas_df)
                    score = get_granularity_weight(user_area, areas_df) * 0.4
                    scores.append(score)
                    reasoning.append(f"Hierarchical match: {child_name} (funder) within {user_area_name} (user)")
                
                #no match
                else:
                    scores.append(0.0)
                    reasoning.append(f"No match: {user_area_name}")
    
    matched_scores = [s for s in scores if s > 0]
    if len(matched_scores) > 0:
        score = sum(matched_scores) / len(matched_scores)
    else:
        score = 0.0
    
    return max(0.0, score), reasoning

def check_beneficiaries(funder_list, user_list):
    """
    Calculates a score based on matches between the funder's and user's stated beneficiaries.
    """

    #define categories and filter
    high_level_bens = {"Other Defined Groups", "The General Public/mankind"}
    exclude_bens = {"Other Charities Or Voluntary Bodies"}
    funder_bens = [ben for ben in funder_list if ben not in exclude_bens]
    user_bens = [ben for ben in user_list if ben not in exclude_bens]
    
    #avoid zero division
    if len(user_bens) == 0:
        return 0.0, []
    
    #categorise funder beneficiaries
    funder_specific = set(ben for ben in funder_bens if ben not in high_level_bens)
    has_high_level = any(ben in high_level_bens for ben in funder_bens)
    
    scores = []
    reasoning = []
    for user_ben in user_bens:
        if user_ben in funder_specific:
            scores.append(1.0)
            reasoning.append(f"Exact match: {user_ben}")
        elif has_high_level:
            scores.append(0.2)
            reasoning.append(f"Weak match: user states '{user_ben}' and funder supports broad categories")
        else:
            scores.append(0.0)
            reasoning.append(f"No match: {user_ben}")
    
    matched_scores = [s for s in scores if s > 0]
    if len(matched_scores) > 0:
        score = sum(matched_scores) / len(matched_scores)
    else:
        score = 0.0

    return max(0.0, score), reasoning

def check_causes(funder_list, user_list):
    """
    Calculates a score based on matches between the funder's and user's stated causes.
    """
    #define categories and filter
    gcp = "General Charitable Purposes"
    exclude_causes = {"Other Charitable Purposes"}
    funder_causes = [cause for cause in funder_list if cause not in exclude_causes]
    user_causes = [cause for cause in user_list if cause not in exclude_causes]
    
    #avoid zero division
    if len(user_causes) == 0:
        return 0.0, []
    
    #categorise funder causes
    funder_specific = set(cause for cause in funder_causes if cause != gcp)
    has_gcp = gcp in funder_causes
    
    scores = []
    reasoning = []
    
    for user_cause in user_causes:
        if user_cause in funder_specific:
            scores.append(1.0)
            reasoning.append(f"Exact match: {user_cause}")
        elif has_gcp:
            scores.append(0.6)
            reasoning.append(f"Weak match: user states '{user_cause}' and funder supports general charitable purposes")
        else:
            scores.append(0.0)
            reasoning.append(f"No match: {user_cause}")
    
    matched_scores = [s for s in scores if s > 0]
    if len(matched_scores) > 0:
        score = sum(matched_scores) / len(matched_scores)
    else:
        score = 0.0
    
    return max(0.0, score), reasoning

def check_keywords(funder_keywords, user_keywords, model):
    """
    Calculates semantic similarity between funder (extracted) and user (inputted) keywords.
    """
    
    #parse json
    if isinstance(funder_keywords, str):
        funder_keywords = json.loads(funder_keywords)
    if isinstance(user_keywords, str):
        user_keywords = json.loads(user_keywords)
    
    #handle empty/nans
    if not funder_keywords:
        funder_keywords = []
    if not user_keywords:
        user_keywords = []
    
    if len(funder_keywords) == 0 or len(user_keywords) == 0:
        return 0.0, {}, ["No keywords to compare"], False
    
    #create embeddings for each keyword
    funder_keywords_em = {}
    for keyword in funder_keywords:
        embedding = model.encode(keyword)
        funder_keywords_em[keyword] = embedding

    user_keywords_em = {}
    for keyword in user_keywords:
        embedding = model.encode(keyword)
        user_keywords_em[keyword] = embedding

    #compare every funder keyword to every user keyword
    all_scores = []
    for funder_kw, funder_em in funder_keywords_em.items():
        for user_kw, user_em in user_keywords_em.items():
            similarity = calculate_similarity_score(funder_em, user_em)
            all_scores.append({
                "funder_keyword": funder_kw,
                "user_keyword": user_kw,
                "similarity": similarity
            })
    
    #sort and check for bonus (matches >= 0.9)
    all_scores.sort(key=lambda x: x["similarity"], reverse=True)
    gets_bonus = any(match["similarity"] >= 0.90 for match in all_scores)
    
    #get dictionary of matches >= 0.90
    strong_matches = {}
    for match in all_scores:
        if match["similarity"] >= 0.90:
            key = f"{match['funder_keyword']} & {match['user_keyword']}"
            strong_matches[key] = match["similarity"]
    
    #filter to top 10 matches <= 0.90 and get average
    scores_under_80 = [match for match in all_scores if match["similarity"] < 0.90]
    top_10 = scores_under_80[:10]

    if len(top_10) > 0:
        score = sum(match["similarity"] for match in top_10) / len(top_10)
    else:
        score = 0.0
    
    #build reasoning from medium matches
    reasoning = []
    for match in scores_under_80[:9]:
        reasoning.append(f"'{match['funder_keyword']}' & '{match['user_keyword']}': {match['similarity']:.3f}")
    
    return max(0.0, score), strong_matches, reasoning, gets_bonus

def check_name_rp(recipients_embedding_dict, user_embedding, user_name):
    """
    Calculates semantic similarity between the user's name and the names of the funder's previous recipients.
    """

    #handle empty/nan
    score = 0.0
    reasoning = []

    #compare every recipient name to the user's name
    all_scores = []
    for recipient_name, recipient_embedding in recipients_embedding_dict.items():
        if recipient_name != user_name:
            similarity = calculate_similarity_score(recipient_embedding, user_embedding)
            all_scores.append({
                "recipient_name": recipient_name,
                "similarity": similarity
            })

    #sort and calculate average of top 10
    all_scores.sort(key=lambda x: x["similarity"], reverse=True)
    top_10 = all_scores[:10]
    if len(top_10) > 0:
        score = sum(match["similarity"] for match in top_10) / len(top_10)
    else:
        score = 0.0

    #build reasoning from top 10 matches
    reasoning = []
    for match in top_10:
        reasoning.append(f"{match['recipient_name']}: {match['similarity']:.3f}")

    return max(0.0, score), reasoning

def check_grants_rp(grants_embedding_dict, user_embedding, user_name):
    """
    Calculates semantic similarity between the user's text sections and the funder's previous grants.
    """

    #handle empty/nan
    score = 0.0
    reasoning = []

    #compare every grant to the user's text
    all_scores = []
    for grant_recipient_name, grant_embedding in grants_embedding_dict.items():
        if grant_recipient_name != user_name:
            similarity = calculate_similarity_score(grant_embedding, user_embedding)
            all_scores.append({
                "grant_recipient_name": grant_recipient_name,
                "similarity": similarity
            })

    #sort and calculate average of top 10
    all_scores.sort(key=lambda x: x["similarity"], reverse=True)
    top_10 = all_scores[:10]
    if len(top_10) > 0:
        score = sum(match["similarity"] for match in top_10) / len(top_10)
    else:
        score = 0.0

    #build reasoning from top 10 matches
    reasoning = []
    for match in top_10:
        reasoning.append(f"{match['grant_recipient_name']}: {match['similarity']:.3f}")

    return max(0.0, score), reasoning

def check_recipients_rp(recipients_embedding_dict, user_embedding, user_name):
    """
    Calculates semantic similarity between the user's text sections and those of the funder's previous recipients.
    """

    #handle empty/nan
    score = 0.0
    reasoning = []

    #compare every recipient's text to the user's text
    all_scores = []
    for recipient_name, recipient_embedding in recipients_embedding_dict.items():
        if recipient_name != user_name:
            similarity = calculate_similarity_score(recipient_embedding, user_embedding)
            all_scores.append({
                "grant_recipient_name": recipient_name,
                "similarity": similarity
            })

    #sort and calculate average of top 10
    all_scores.sort(key=lambda x: x["similarity"], reverse=True)
    top_10 = all_scores[:10]
    if len(top_10) > 0:
        score = sum(match["similarity"] for match in top_10) / len(top_10)
    else:
        score = 0.0

    #build reasoning from top 10 matches
    reasoning = []
    for match in top_10:
        reasoning.append(f"{match['grant_recipient_name']}: {match['similarity']:.3f}")

    return max(0.0, score), reasoning

def calculate_keywords_bonus(strong_matches, ukcat_df):
    """
    Calculates bonus based on keyword matches. Only runs if keywords with semantic scores above 0.8 exist.
    """

    #weight by specificity of ukcat level
    level_weights = {
        1: 0.3, 
        2: 0.7, 
        3: 1.0
    }
    
    weighted_scores = []
    for keyword, score in strong_matches.items():
        #find keyword in ukcat_df
        match = ukcat_df[ukcat_df['tag'].str.upper() == keyword.upper()]
        
        if not match.empty:
            level = match.iloc[0]['level']
            weighted_score = score * level_weights.get(level, 1.0)
        else:
            weighted_score = score * 0.3
        
        weighted_scores.append(weighted_score)
    
    avg_weighted = sum(weighted_scores) / len(weighted_scores)
    
    #calculate bonus
    bonus = 1.1 + (avg_weighted * 0.2)
    bonus = min(max(bonus, 1.1), 1.3)
    
    return bonus

def calculate_relationship_bonus(relationship_df):
    """
    Calculates time since last grant and calculates a bonus. Only runs if there is a relationship.
    """

    #get time lapsed since last gift
    last_grant_year = relationship_df["year"].max()
    current_year = datetime.now().year
    time_lapsed = current_year - last_grant_year
    
    #assign bands
    if time_lapsed <= 2:
        bonus = 1.5
    elif time_lapsed <= 3:
        bonus = 1.4
    elif time_lapsed <= 5:
        bonus = 1.3
    elif time_lapsed <= 10:
        bonus = 1.2
    else:
        bonus = 1.1
    
    #add uplift for recurring relationship
    num_grants = len(relationship_df)
    if num_grants >= 5:
        bonus += 0.1
    
    return time_lapsed, bonus, last_grant_year

def calculate_areas_bonus_rp(funder_grants_df, user_areas, areas_df, hierarchies_df):
    """
    Calculates a bonus based on how well the user's areas match the funder's recipient's areas.
    """

    if funder_grants_df.empty:
        return 0.0, ["No grants history available"]

    #get unique areas from recipients
    all_areas = []
    for areas_list in funder_grants_df["recipient_areas"]:
        if isinstance(areas_list, list):
            all_areas.extend(areas_list)

    if len(all_areas) == 0:
        return 0.0, ["No area data available"]

    recipient_areas = list(set(all_areas))

    #check areas
    match_score, _ = check_areas(recipient_areas, user_areas, areas_df, hierarchies_df)

    #convert to bonus multiplier
    bonus = 1.0 + (match_score * 0.2)

    #get reasoning from top 10 (low level tiers only)
    area_count = {}
    for area_name in all_areas:
        area_id = get_id_from_name(area_name, areas_df)
        if area_id:
            granularity = get_granularity_weight(area_id, areas_df)
            if granularity >= 0.9:
                area_count[area_name] = area_count.get(area_name, 0) + 1

    if len(area_count) == 0:
        reasoning = ["Only broad geographic areas found"]
    else:
        sorted_areas = sorted(area_count.items(), key=lambda x: x[1], reverse=True)
        total_low_level = sum(area_count.values())

        reasoning = []
        for area_name, count in sorted_areas[:10]:
            percentage = (count / total_low_level) * 100
            reasoning.append(f"{area_name}: {count} grants ({percentage:.1f}%)")

    return bonus, reasoning

def calculate_keywords_bonus_rp(funder_grants_df, user_keywords):
    """
    Calculates a bonus based on exact keyword matches between user and funder's recipients.
    """

    if funder_grants_df.empty:
        return 1.0, ["No grants history available"]

    #parse json
    if isinstance(user_keywords, str):
        user_keywords = json.loads(user_keywords)
    if not user_keywords:
        user_keywords = []

    if len(user_keywords) == 0:
        return 1.0, ["No user keywords to match"]

    #get all recipient keywords
    all_recipient_keywords = []
    for recipient_keywords in funder_grants_df["recipient_extracted_class"]:
        if isinstance(recipient_keywords, str):
            recipient_keywords = json.loads(recipient_keywords)
        if recipient_keywords:
            all_recipient_keywords.extend(recipient_keywords)

    if len(all_recipient_keywords) == 0:
        return 1.0, ["No recipient keywords available"]

    #find exact matches and count frequency
    matched_keywords = {}
    user_keywords_matched = set()

    for user_kw in user_keywords:
        if user_kw in all_recipient_keywords:
            user_keywords_matched.add(user_kw)
            matched_keywords[user_kw] = matched_keywords.get(user_kw, 0) + all_recipient_keywords.count(user_kw)

    #calculate match percentage
    match_percentage = len(user_keywords_matched) / len(user_keywords)

    #calculate bonus
    if match_percentage >= 0.9:
        bonus = 1.1
    elif match_percentage >= 0.5:
        bonus = 1.05
    else:
        bonus = 1.0 + (match_percentage * 0.2)

    #build reasoning from top 10
    if len(matched_keywords) == 0:
        reasoning = ["No exact keyword matches found"]
    else:
        sorted_matches = sorted(matched_keywords.items(), key=lambda x: x[1], reverse=True)

        reasoning = []
        for keyword, count in sorted_matches[:10]:
            reasoning.append(f"{keyword}: {count} occurrences")

    return bonus, reasoning

def calculate_lv_penalty(funder_grants_df):
    """
    Identifies low variance in a funder's previous giving and calculates a penalty.
    """

    #skip funders with low giving history
    if len(funder_grants_df) < 10:
        return 1.0

    total_grants = len(funder_grants_df)
    unique_recipients = funder_grants_df['recipient_name'].nunique()
    
    #find proportion of grants to unique recipients
    variance_proportion = unique_recipients / total_grants
    
    #calculate penalty
    if variance_proportion < 0.3:
        penalty = 0.7
    else:
        penalty = 1.0
    
    return penalty

