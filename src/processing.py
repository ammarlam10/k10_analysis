import pandas as pd
import numpy as np
from scipy.spatial.distance import cdist
import ast
import io







def calculate_cosine(df):

    df['Embed'] = df['Embeddings'].apply(ast.literal_eval)

    ids = df['ID'].tolist()
    embeddings_array = np.vstack(df['Embed'].apply(np.asarray))
    distance_matrix = cdist(embeddings_array, embeddings_array, metric='cosine')
    similarity_matrix = 1 - distance_matrix

    similarity_df = pd.DataFrame(similarity_matrix)
    similarity_df.index = ids
    similarity_df.columns = ids

    return similarity_df


def transform_similarity_df_to_match_stats(
    cosine_similarity_df: pd.DataFrame,
    hist_corr_mean: float,
    hist_corr_std: float,
    use_tanh_clipping: bool = True,
    tanh_scaling_factor: float = 2.5  # Adjusted default for better tanh spread
) -> pd.DataFrame:
    """
    Transforms a cosine similarity DataFrame to have a similar mean and standard deviation
    to historical return correlations, with optional tanh clipping.

    Args:
        cosine_similarity_df (pd.DataFrame): A square DataFrame of cosine similarities.
                                             Diagonal should ideally be 1.0.
        hist_corr_mean (float): The target mean (from historical correlations).
        hist_corr_std (float): The target standard deviation (from historical correlations).
        use_tanh_clipping (bool): If True, uses np.tanh for clipping to [-1, 1].
                                 If False, uses np.clip.
        tanh_scaling_factor (float): A factor to scale values before applying tanh.
                                     This controls how "saturated" tanh becomes.
                                     Default 2.5 often gives a reasonable spread for tanh.

    Returns:
        pd.DataFrame: The transformed DataFrame with original index and columns.
    """
    if cosine_similarity_df.shape[0] != cosine_similarity_df.shape[1]:
        raise ValueError("Cosine similarity DataFrame must be square.")
    if not np.all(cosine_similarity_df.index == cosine_similarity_df.columns):
        print("Warning: DataFrame index and columns do not match. Assuming they correspond by position.")

    original_index = cosine_similarity_df.index
    original_columns = cosine_similarity_df.columns
    similarity_matrix_np = cosine_similarity_df.values.copy() # Work on a copy

    N = similarity_matrix_np.shape[0]

    if N == 0:
        return pd.DataFrame(index=original_index, columns=original_columns)
    if N == 1: # Single asset, self-correlation is 1
        return pd.DataFrame(np.array([[1.0]]), index=original_index, columns=original_columns)

    # Create a mask for off-diagonal elements
    off_diagonal_mask = ~np.eye(N, dtype=bool)
    sim_scores_off_diagonal = similarity_matrix_np[off_diagonal_mask]

    if len(sim_scores_off_diagonal) == 0 :

        print("Warning: No off-diagonal elements found for N > 1. Check matrix structure.")
        rescaled_matrix = np.full_like(similarity_matrix_np, hist_corr_mean)
    else:
        sim_mean = np.mean(sim_scores_off_diagonal)
        sim_std = np.std(sim_scores_off_diagonal)
        
        print(f"Original Similarity (Off-diagonal): Mean={sim_mean:.4f}, Std={sim_std:.4f}, Min={np.min(sim_scores_off_diagonal):.4f}, Max={np.max(sim_scores_off_diagonal):.4f}")

        if sim_std == 0 or np.isnan(sim_std): # Handles N > 1 with all same off-diagonal values
            print("Warning: Standard deviation of original similarity scores is 0 or NaN. All off-diagonal scores might be identical.")
            rescaled_matrix = np.full_like(similarity_matrix_np, hist_corr_mean)
        else:
            standardized_matrix = (similarity_matrix_np - sim_mean) / sim_std
            rescaled_matrix = (standardized_matrix * hist_corr_std) + hist_corr_mean
    
    # Clipping
    if use_tanh_clipping:
        clipped_matrix = np.tanh(rescaled_matrix * tanh_scaling_factor)
    else:
        clipped_matrix = np.clip(rescaled_matrix, -1.0, 1.0)

    np.fill_diagonal(clipped_matrix, 1.0)
    
    clipped_matrix = (clipped_matrix + clipped_matrix.T) / 2.0
    
    final_off_diagonal_scores = clipped_matrix[off_diagonal_mask]
    if len(final_off_diagonal_scores) > 0:
        final_mean = np.mean(final_off_diagonal_scores)
        final_std = np.std(final_off_diagonal_scores)
        print(f"Transformed (Off-diagonal): Mean={final_mean:.4f}, Std={final_std:.4f}, Min={np.min(final_off_diagonal_scores):.4f}, Max={np.max(final_off_diagonal_scores):.4f}")
    else: 
         pass 

    return pd.DataFrame(clipped_matrix, index=original_index, columns=original_columns)