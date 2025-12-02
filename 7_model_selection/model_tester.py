import pandas as pd
from sentence_transformers import SentenceTransformer, util
import time

def test_embedding_models(
    models_list,
    funders_df,
    recipients_df,
    embedding_pairs,
    funder_text_col="funders_text",
    recipient_text_col="recipients_text",
    rating_col="my_rating"
):
    """
    Tests various embedding models and calculate the correlation with their output and my own ratings of funder-recipient pairs.
    """
    results = []
    current_pairs = embedding_pairs.copy()
    overall_start = time.time()

    for model_name in models_list:
        model_start = time.time()
        model = SentenceTransformer(model_name)

        #align pairs
        aligned_pairs = current_pairs.merge(
            funders_df[["registered_num", funder_text_col]],
            left_on="funder_registered_num",
            right_on="registered_num",
            how="left"
        ).merge(
            recipients_df[["recipient_id", recipient_text_col]],
            on="recipient_id",
            how="left"
        )

        #make embeddings
        funders_ems = model.encode(aligned_pairs[funder_text_col].tolist())
        recipients_ems = model.encode(aligned_pairs[recipient_text_col].tolist())

        #calculate similarities
        similarities = []
        for i in range(len(aligned_pairs)):
            similarity = util.cos_sim(funders_ems[i], recipients_ems[i]).item()
            similarities.append(similarity)

        current_pairs[f"{model_name}_sim"] = similarities

        #calculate correlation with ratings
        corr = current_pairs[rating_col].corr(current_pairs[f"{model_name}_sim"])

        results.append({
            "model": model_name,
            "correlation": corr
        })

        model_time = time.time() - model_start
        print(f"{model_name}: {model_time:.1f}s")

    results_df = pd.DataFrame(results)

    total_time = time.time() - overall_start
    print(f"\nTotal test time: {total_time:.1f}s")

    return results_df, current_pairs

