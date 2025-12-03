import pandas as pd
from sentence_transformers import SentenceTransformer, util
import time

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

    #concatenate if necessary
    funders_to_test["text_to_embed"] = funders_to_test[funder_text_cols[0]].fillna("")
    for col in funder_text_cols[1:]:
        funders_to_test["text_to_embed"] += " " + funders_to_test[col].fillna("")

    recipients_to_test["text_to_embed"] = recipients_to_test[recipient_text_cols[0]].fillna("")
    for col in recipient_text_cols[1:]:
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
