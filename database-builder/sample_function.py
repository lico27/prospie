import pandas as pd
import os

def get_sample():

    """
    Gets data from CSVs and calculates sizes for proportional sampling. Gets sample of charity numbers to use for prototype.
    """

    target = 500
    total = 15271

    #get path for data files
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(current_dir, "data")

    file_names = [
        os.path.join(data_dir, "0-49k.csv"),
        os.path.join(data_dir, "50k-99k.csv"),
        os.path.join(data_dir, "100k-199k.csv"),
        os.path.join(data_dir, "200k-499k.csv"),
        os.path.join(data_dir, "500k-1m.csv"),
        os.path.join(data_dir, "1m.csv")
    ]
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
    