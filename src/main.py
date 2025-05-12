# project_root/src/main.py

import argparse
import logging
import os
import sys
import random
import pandas as pd
from data_handler import load_data, convert_to_pandas
from summarization import call_chatgpt_api
from embedding import generate_embedding
import openai
from processing import calculate_cosine, transform_similarity_df_to_match_stats

from config_loader import load_config

def main():
    """
    Main function to orchestrate the 10-K filing similarity analysis workflow.
    Handles configuration loading, data processing, and output/reporting.
    """

    conf = load_config()
    # Load data currently as a pickle file
    # data = load_data()

    # Convert to df for easy manipulation 
    # df = convert_to_pandas(data)
    
    # Get Summary
    # for index, row in df.iterrows():
    #     print(row['ID'], index)
    #     print("-----------------")
    #     text = row['Business'] + " " + row['Risk']
    #     df.loc[index,'Summary'] = call_chatgpt_api(filing_text=text,api_key=conf['openai_api_key'],model=conf['summarization_model'])

    # df.to_csv('/home/ammar/Desktop/k10 filing/data/output/data_with_summary.csv')
    # df = pd.read_csv('/home/ammar/Desktop/k10 filing/data/output/data_with_summary.csv')
    # Convert summary to list
    # input = [i for i in df['Summary']]
    # Get embeddings
    # embeddings = generate_embedding(text_input=input, model=conf['embedding_model'], OPENAI_API_KEY = conf['openai_api_key'],client = openai.OpenAI(api_key=conf['openai_api_key']))
    # df['Embeddings'] = embeddings
    # df.to_csv('/home/ammar/Desktop/k10 filing/data/output/data_with_summary_embeddings_small.csv')
    # Create Cosine similarity and correlation matrix
    # df = pd.read_csv("/home/ammar/Desktop/k10 filing/data/output/data_with_summary_embeddings.csv")
    # out = calculate_cosine(df)
    # df = pd.read_csv("/home/ammar/Desktop/k10 filing/data/output/Cosine_similarity.csv")
    # del df['Unnamed: 0']
    
    # Transform similarity based on mean and std with tanh scaling
    out2 = transform_similarity_df_to_match_stats(df,
                                                  0.45,
                                                  0.25,
                                                  use_tanh_clipping=True,
                                                  tanh_scaling_factor=1.0 )
    print("DONE")

if __name__ == "__main__":
    main()