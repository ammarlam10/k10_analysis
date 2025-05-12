import requests
import json
import os 

def call_chatgpt_api(filing_text, api_key, model="o4-mini", system_message=None):
    """
    Calls the OpenAI Chat Completions API with the given text input.

    Args:
        text_input (str): The main text to send as the user's message.
        api_key (str): Your OpenAI API key.
        model (str): The OpenAI model to use (e.g., "gpt-3.5-turbo", "gpt-4").
                     See OpenAI documentation for available models.
        system_message (str, optional): An optional system message to provide context
                                        or instructions to the model. Defaults to None.

    Returns:
        str or None: The text response from the API, or None if the call fails.
    """
    api_url = "https://api.openai.com/v1/chat/completions"

    text_input = f"""
    Summarize the "Business" and "Risk Factors" sections of a company's 10-K filing (attached at the end). The summary should capture the key points and essential information from each section to facilitate the creation of embeddings for a similarity matrix.

    Steps
    Read the "Business" Section:

    Identify the main business activities, products, or services offered by the company.
    Note any significant markets or customer segments the company serves.
    Highlight any unique business strategies or competitive advantages.

    Read the "Risk Factors" Section:

    Identify the primary risks that could impact the company's operations or financial performance.
    Note any industry-specific risks or regulatory challenges.
    Highlight any significant financial, operational, or strategic risks mentioned.

    Summarize:
    Create a concise summary, ensuring that all key points are covered.
    Maintain a neutral and factual tone, focusing on the most relevant information.

    Output Format

    Provide a summary in paragraph form, approximately 750 - 1000 words in total, capturing the essence of the respective section.

    Notes
    Ensure that the summary is objective and does not include personal opinions or interpretations.
    Focus on clarity and conciseness.

    Text:
    {filing_text}
    """

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    messages = []
    if system_message:
        messages.append({"role": "system", "content": system_message})

    messages.append({"role": "user", "content": text_input})

    payload = {
        "model": model,
        "messages": messages,
    }

    print(f"Sending request to OpenAI API (Model: {model})...")

    try:
        response = requests.post(api_url, headers=headers, json=payload)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

        data = response.json()

        if data and 'choices' in data and len(data['choices']) > 0:
            return data['choices'][0]['message']['content'].strip()
        else:
            print("API response structure unexpected or empty choices.")
            print("Response Data:", data) # Print response data for debugging
            return None

    except requests.exceptions.RequestException as e:
        print(f"OpenAI API request failed: {e}")
        if e.response is not None:
            print(f"Status Code: {e.response.status_code}")
            try:
                 error_details = e.response.json()
                 print(f"Error Details: {error_details}")
            except json.JSONDecodeError:
                 print(f"Raw response body: {e.response.text}") # Fallback if response isn't JSON
        return None
    except json.JSONDecodeError:
        print("Failed to parse JSON response from OpenAI API.")
        if 'response' in locals() and response is not None:
             print("Raw response text:", response.text)
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

    

