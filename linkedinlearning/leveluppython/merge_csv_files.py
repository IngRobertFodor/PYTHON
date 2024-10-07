import pandas as pd # type: ignore


# Function to merge two csv files
def merge_csv_files(df_one, df_two, merged_df):

    read_df_one = pd.read_csv(df_one, sep=";")
    print(read_df_one)
    read_df_two = pd.read_csv(df_two, sep=";")
    print(read_df_two)
    merged_df = pd.merge(read_df_one, read_df_two, on="Username", how="inner", suffixes=('_one', '_two'))
    merged_df.to_csv("merged_csv_files.csv", index=False)
    
    return merged_df


print(merge_csv_files("csv_file_one.csv", "csv_file_two.csv", "merged_csv_files.csv"))