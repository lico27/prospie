# Checkpoints

This folder (locally) contains seven pickle files: 
1. `funders_df.pkl`, `recipients_df.pkl`, `grants_df.pkl` and `areas_df.pkl`. These files contain the dataframes used in the data preparation notebook and have been saved before the embedding and feature creation processes take place.
2. `funders_df_em.pkl`, `recipients_df_em.pkl` and `grants_em.pkl`. These files contain the dataframes after keyword matching and after the embeddings have been created for the selected text columns, to avoid having to rerun the these processes.