import pandas as pd

def get_sample():
    
    """
    Gets data from CSVs and calculates sizes for proportional sampling. Gets sample of charity numbers to use for prototype.
    """

    target = 20
    total = 15271
    file_names = ["./data/0-49k.csv", "./data/50k-99k.csv", "./data/100k-199k.csv", "./data/200k-499k.csv", "./data/500k-1m.csv", "./data/1m.csv"]
    dataframes = {}
    sample_sizes = {}
    df_all = pd.DataFrame()

    #read in csvs
    for i, file_name in enumerate(file_names):
        dataframe_name = f"df_{chr(ord('a') + i)}"
        dataframes[dataframe_name] = pd.read_csv(file_name)  

    #get sample sizes
    for i, df in enumerate(dataframes.values()):
        sample_name = f"df_{chr(ord('a') + i)}_sample"
        df_sample = int(len(df) / total * target)

        #save for reference
        sample_sizes[sample_name] = df_sample

        #get proportional sample
        dataframes[f"df_{chr(ord('a') + i)}"] = df.sample(n=sample_sizes[f"df_{chr(ord('a') + i)}_sample"], random_state=42)

    #combine dfs
    for df in dataframes.values():
        df_all = pd.concat([df_all, df], ignore_index=True) 

    #build list of charity numbers
    c_nums = df_all["Charity Number"].astype(str).tolist()

    return c_nums, sample_sizes
    