import pandas as pd
from sentence_transformers import SentenceTransformer, util
import time

#define constants
RECIPIENTS_SECTIONS = ["recipient_activities", "recipient_objectives"]
COMBINATIONS_DICT = {
    # --- 2-column combinations ---
    "acts_objs": (["activities", "objectives"], RECIPIENTS_SECTIONS),
    "acts_objacts": (["activities", "objectives_activities"], RECIPIENTS_SECTIONS),
    "acts_achs": (["activities", "achievements_performance"], RECIPIENTS_SECTIONS),
    "acts_policy": (["activities", "grant_policy"], RECIPIENTS_SECTIONS),

    "objs_objacts": (["objectives", "objectives_activities"], RECIPIENTS_SECTIONS),
    "objs_achs": (["objectives", "achievements_performance"], RECIPIENTS_SECTIONS),
    "objs_policy": (["objectives", "grant_policy"], RECIPIENTS_SECTIONS),

    # --- 3-column combinations ---
    "acts_objs_objacts": (
        ["activities", "objectives", "objectives_activities"], RECIPIENTS_SECTIONS
    ),
    "acts_objs_achs": (
        ["activities", "objectives", "achievements_performance"], RECIPIENTS_SECTIONS
    ),
    "acts_objs_policy": (
        ["activities", "objectives", "grant_policy"], RECIPIENTS_SECTIONS
    ),
    "acts_objacts_achs": (
        ["activities", "objectives_activities", "achievements_performance"], RECIPIENTS_SECTIONS
    ),
    "acts_objacts_policy": (
        ["activities", "objectives_activities", "grant_policy"], RECIPIENTS_SECTIONS
    ),
    "acts_achs_policy": (
        ["activities", "achievements_performance", "grant_policy"], RECIPIENTS_SECTIONS
    ),

    "objs_objacts_achs": (
        ["objectives", "objectives_activities", "achievements_performance"], RECIPIENTS_SECTIONS
    ),
    "objs_objacts_policy": (
        ["objectives", "objectives_activities", "grant_policy"], RECIPIENTS_SECTIONS
    ),
    "objs_achs_policy": (
        ["objectives", "achievements_performance", "grant_policy"], RECIPIENTS_SECTIONS
    ),

    # --- 4-column combinations ---
    "acts_objs_objacts_achs": (
        ["activities", "objectives", "objectives_activities", "achievements_performance"], RECIPIENTS_SECTIONS
    ),
    "acts_objs_objacts_policy": (
        ["activities", "objectives", "objectives_activities", "grant_policy"], RECIPIENTS_SECTIONS
    ),
    "acts_objs_achs_policy": (
        ["activities", "objectives", "achievements_performance", "grant_policy"], RECIPIENTS_SECTIONS
    ),
    "acts_objacts_achs_policy": (
        ["activities", "objectives_activities", "achievements_performance", "grant_policy"], RECIPIENTS_SECTIONS
    ),
    "objs_objacts_achs_policy": (
        ["objectives", "objectives_activities", "achievements_performance", "grant_policy"], RECIPIENTS_SECTIONS
    ),
}

def test_embedding_approach(
    model_name,
    funders_df,
    recipients_df,
    embedding_pairs,
    funder_text_cols,
    recipient_text_cols,
    approach,
    rating_col="my_rating"
):
    """
    Tests a specific approach to embedding and comparing text columns.
    """

    start_time = time.time()
    model = SentenceTransformer(model_name)
    funders_to_test = funders_df.copy()
    recipients_to_test = recipients_df.copy()

    #handle single strings
    if isinstance(funder_text_cols, str):
        funder_text_cols = [funder_text_cols]
    if isinstance(recipient_text_cols, str):
        recipient_text_cols = [recipient_text_cols]

    #check cols are available
    available_funder_cols = [col for col in funder_text_cols if col in funders_to_test.columns]
    available_recipient_cols = [col for col in recipient_text_cols if col in recipients_to_test.columns]

    #raise error if no columns are available
    if len(available_funder_cols) == 0:
        raise ValueError(f"Funder does not have {funder_text_cols}. Try {funders_to_test.columns.tolist()}")
    if len(available_recipient_cols) == 0:
        raise ValueError(f"Recipient does not have {recipient_text_cols}. Try {recipients_to_test.columns.tolist()}")

    #concatenate if necessary
    funders_to_test["text_to_embed"] = funders_to_test[available_funder_cols[0]].fillna("")
    for col in available_funder_cols[1:]:
        funders_to_test["text_to_embed"] += " " + funders_to_test[col].fillna("")

    recipients_to_test["text_to_embed"] = recipients_to_test[available_recipient_cols[0]].fillna("")
    for col in available_recipient_cols[1:]:
        recipients_to_test["text_to_embed"] += " " + recipients_to_test[col].fillna("")

    #make lowercase
    funders_to_test["text_to_embed"] = funders_to_test["text_to_embed"].str.lower()
    recipients_to_test["text_to_embed"] = recipients_to_test["text_to_embed"].str.lower()

    #align pairs
    aligned_pairs = embedding_pairs.merge(
        funders_to_test[["registered_num", "text_to_embed"]],
        left_on="funder_registered_num",
        right_on="registered_num",
        how="left"
    ).rename(columns={"text_to_embed": "funder_text"})

    aligned_pairs = aligned_pairs.merge(
        recipients_to_test[["recipient_id", "text_to_embed"]],
        on="recipient_id",
        how="left"
    ).rename(columns={"text_to_embed": "recipient_text"})

    #make embeddings
    funders_ems = model.encode(aligned_pairs["funder_text"].tolist())
    recipients_ems = model.encode(aligned_pairs["recipient_text"].tolist())

    #calculate similarities
    similarities = []
    for i in range(len(aligned_pairs)):
        similarity = util.cos_sim(funders_ems[i], recipients_ems[i]).item()
        similarities.append(similarity)

    #calculate correlation with ratings
    correlation = embedding_pairs[rating_col].corr(pd.Series(similarities))

    execution_time = time.time() - start_time

    print(f"{approach}: r={correlation:.3f}, time={execution_time:.1f}s")

    return similarities, correlation, execution_time


def compare_approaches(
    model_name,
    funders_df,
    recipients_df,
    embedding_pairs,
    approaches_dict,
    rating_col="my_rating"
):
    """
    Compares approaches and summarises the results.
    """
    results = []
    pairs_with_scores = embedding_pairs.copy()
    overall_start = time.time()

    for approach, (funder_cols, recipient_cols) in approaches_dict.items():
        similarities, correlation, exec_time = test_embedding_approach(
            model_name=model_name,
            funders_df=funders_df,
            recipients_df=recipients_df,
            embedding_pairs=embedding_pairs,
            funder_text_cols=funder_cols,
            recipient_text_cols=recipient_cols,
            rating_col=rating_col,
            approach=approach
        )

        #add similarities to pairs df
        pairs_with_scores[f"{approach}_sim"] = similarities

        results.append({
            "approach": approach,
            "funder_columns": " + ".join(funder_cols),
            "recipient_columns": " + ".join(recipient_cols),
            "correlation": correlation,
            "time_seconds": exec_time
        })

    results_df = pd.DataFrame(results)
    total_time = time.time() - overall_start

    print(f"\nTotal time: {total_time:.1f}s")
    print(f"Best approach: {results_df.loc[results_df['correlation'].idxmax(), 'approach']} "
          f"(r={results_df['correlation'].max():.3f})")

    return results_df, pairs_with_scores
