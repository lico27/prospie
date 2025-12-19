





def check_name_rp(recipients_embedding_dict, user_embedding, user_name):
    """
    Calculates semantic similarity between the user's name and the names of the funder's previous recipients.
    """

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

    return score, reasoning

def check_grants_rp(grants_embedding_dict, user_embedding, user_name):
    """
    Calculates semantic similarity between the user's text sections and the funder's previous grants.
    """

    #compare every grant to the user's text
    all_scores = []
    for grant_recipient_name, grant_embedding in grants_embedding_dict.items():
        if grant_recipient_name != user_name:
            similarity = calculate_similarity_score(grant_embedding, user_embedding)
            all_scores.append({
                "grant_info": grant_recipient_name,
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
        reasoning.append(f"{match['grant_info']}: {match['similarity']:.3f}")

    return score, reasoning
