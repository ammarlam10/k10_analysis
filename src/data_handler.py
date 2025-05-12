import pickle
import os 
import pandas as pd

def load_data(pickle_file_path='/home/ammar/Desktop/k10 filing/data/extracted_sections/extracted_data.p' ):
    # Ensure the file exists before attempting to load
    if not os.path.exists(pickle_file_path):
        print(f"Error: File not found at '{pickle_file_path}'")
    else:
        print(f"Attempting to load data from '{pickle_file_path}'...")
        try:
            # Open the file in binary read mode ('rb')
            with open(pickle_file_path, 'rb') as f:
                # Load the data from the file
                loaded_dictionary = pickle.load(f)

            print(f"Successfully loaded data from '{pickle_file_path}'.")
            print(f"Type of loaded data: {type(loaded_dictionary)}")

            if isinstance(loaded_dictionary, dict):
                print("Loaded data is a dictionary as expected.")
                print(f"Number of items in the dictionary: {len(loaded_dictionary)}")

                print("\nSample items from the loaded dictionary (first 5):")
                count = 0
                for key, value in loaded_dictionary.items():
                    print(f"  Key: {key}, Value (type: {type(value)}): {str(value)[:50]}{'...' if len(str(value)) > 50 else ''}")
                    count += 1
                    if count >= 5:
                        break
                if len(loaded_dictionary) > 5:
                    print("  ...")


            else:
                print("Warning: Loaded data is not a dictionary. Check how the file was saved.")

        except FileNotFoundError:
            print(f"Error: File not found at '{pickle_file_path}'. (Should not happen due to initial check)")
        except (pickle.UnpicklingError, EOFError, Exception) as e:
            print(f"Error loading or unpickling data from '{pickle_file_path}': {e}")
            print("The file might be corrupted or not a valid pickle file.")
        return loaded_dictionary
    
    
def convert_to_pandas(data):
    data_df = {}
    data_df['ID'] = []
    data_df['Business'] = []
    data_df['Risk'] = []
    data_df['Summary'] = []
        
    for k in data.keys():
        data_df['ID'].append(k)
        data_df['Business'].append(data[k][0])
        data_df['Risk'].append(data[k][1])
        data_df['Summary'].append(None)
    return pd.DataFrame.from_dict(data_df)
