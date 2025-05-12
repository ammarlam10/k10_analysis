import os
import openai
from openai import APIError, APIConnectionError, RateLimitError # Import specific exceptions
import time # Import time for potential retries or rate limit handling



def generate_embedding(text_input, model, OPENAI_API_KEY ,client):
    """
    Generates a text embedding vector for the given text using an OpenAI model.

    Args:
        text_input (str or list of str): The text string(s) to embed.
                                        A list is more efficient for multiple texts.
        model (str): The OpenAI embedding model to use.
        OPENAI_API_KEY: OPEN AI KEY
        client (client, optional): Client connection when function is called

    Returns:
        list or None: The embedding vector (a list of floats) if text_input is a single string,
                      or a list of embedding vectors if text_input is a list of strings.
                      Returns None if the API call fails or input is invalid.
    """


    if not text_input:
        print("Error: Input text is empty.")
        return None

    # The API expects string input or a list of strings
    if not isinstance(text_input, (str, list)):
        print(f"Error: Invalid input type: {type(text_input)}. Must be str or list of str.")
        return None
    if isinstance(text_input, list) and not all(isinstance(i, str) for i in text_input):
        print("Error: List input must contain only strings.")
        return None

    print(f"Generating embedding(s) using model '{model}'...")

    try:
        # Call the embeddings creation endpoint
        response = client.embeddings.create(
            input=text_input,
            model=model
            )

        if isinstance(text_input, str):
            # Return the embedding for the single input string
            if response.data and len(response.data) > 0:
                 return response.data[0].embedding
            else:
                 print(f"API returned an unexpected response structure for single input: {response}")
                 return None
        elif isinstance(text_input, list):
             # Return a list of embeddings for the list of input strings
             if response.data and len(response.data) == len(text_input):
                  # Extract the embedding list from each data object
                  return [item.embedding for item in response.data]
             else:
                  print(f"API returned an unexpected response structure for list input: {response}")
                  return None

    except (APIError, APIConnectionError, RateLimitError) as e:
        print(f"OpenAI API error occurred: {e}")
        # Specific error handling based on exception type:
        if isinstance(e, RateLimitError):
             print("Rate limit exceeded. Consider adding retry logic or spacing out calls.")
        elif isinstance(e, APIConnectionError):
             print("Connection error. Check your network or firewall.")
        elif isinstance(e, APIError):
             print(f"API Error: {e.status_code} - {e.response.text}") # More details for API errors
        return None
    except Exception as e:
        print(f"An unexpected error occurred during OpenAI API call: {e}")
        return None
    



