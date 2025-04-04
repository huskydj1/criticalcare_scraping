import pandas as pd
import glob
import re
import os

def extract_range(filename):
    # Extract the numbers from the filename
    match = re.search(r'temp_(\d+)_\d+\.csv$', filename)
    if match:
        return int(match.group(1))
    return None

def main():
    df_articles = pd.read_csv('articles.csv')

    all_data = []
    for file_i, range_i in [
        ("articles_with_authors_temp_0_1766.csv", (0, 160)),
        ("articles_with_authors_temp_160_1766.csv", (160, 445)),
        ("articles_with_authors_temp_445_1766.csv", (445, 570)),
        ("articles_with_authors_temp_570_1766.csv", (570, 819)),
        ("articles_with_authors_temp_819_1766.csv", (819, 1240)),
        ("articles_with_authors_temp_1240_1766.csv", (1240, 1530)),
        ("articles_with_authors_temp_1530_1766.csv", (1530, 1766)),
    ]:
        df_i = pd.read_csv(file_i)
        df_i = df_i.iloc[0 : range_i[1] - range_i[0]]
        all_data.append(df_i)

    combined_df = pd.concat(all_data, ignore_index = True)

    combined_df = combined_df.drop_duplicates()
    # Remove error manually
    combined_df = combined_df[combined_df['Article Title'] != '602: CEFIDEROCOL FOR PSEUDOMONAS BACTEREMIA WITH LEFT VENTRICULAR ASSIST DEVICE']


    combined_df.to_csv('combined.csv', index=False)

    print(len(combined_df), len(df_articles))
    print(len(set(combined_df['Article Title'])), len(set(df_articles['Article Title'])))
    print("ONE")
    print(set(df_articles['Article Title']) - set(combined_df['Article Title']))
    print("TWO")
    print(set(combined_df['Article Title']) - set(df_articles['Article Title']))

    # # Remove duplicates if any
    # original_len = len(combined_df)
    # combined_df = combined_df.drop_duplicates()
    # if len(combined_df) < original_len:
    #     print(f"\nRemoved {original_len - len(combined_df)} duplicate rows")
    
    # # Save combined data
    # output_file = 'articles_with_authors_combined.csv'
    # combined_df.to_csv(output_file, index=False)
    # print(f"\nSaved combined data to {output_file}")
    # print(f"Total rows: {len(combined_df)}")

if __name__ == "__main__":
    main()