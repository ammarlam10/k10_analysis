# project_root/src/extraction.py

import fitz  # PyMuPDF
import re
import os


# Define the exact section headings we expect, using flexible regex for spacing/punctuation
SECTION_PATTERNS = {
    "Item 1. Business": r"Item\s*1\.?\s*Business",
    "Item 1A Risk Factors": r"Item\s*1A\.?\s*Risk\s*Factors",
    "Item 1B. Unresolved Staff Comments": r"Item\s*1B\.?\s*Unresolved\s*Staff\s*Comments",
}

# Define the order of the sections we expect to find them in
SECTION_ORDER = [
    "Item 1. Business",
    "Item 1A Risk Factors",
    "Item 1B. Unresolved Staff Comments",
]

def extract_text_between_specific_sections(pdf_path):
    """
    Extracts text content found between specific, ordered sections in a PDF.
    Specifically targets text between Item 1 and Item 1A, and between Item 1A and Item 1B.

    Args:
        pdf_path (str): The path to the PDF file.

    Returns:
        dict: A dictionary with two keys:
              - "Text between Item 1 and 1A": Text content between the end of Item 1
                                            heading and the start of Item 1A heading.
              - "Text between Item 1A and 1B": Text content between the end of Item 1A
                                            heading and the start of Item 1B heading.
              Returns an empty dictionary if the PDF cannot be opened or the
              required sections are not found in the expected order.
    """
    extracted_content = {}
    doc = None  # Initialize doc to None

    try:
        doc = fitz.open(pdf_path)
        total_text = ""
        # Extract text page by page - more reliable than doc.get_text() sometimes
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            if 'part i'.lower() in page.get_text().lower() and 'part iv'.lower() in page.get_text().lower():
                print('found on ',page )
                return
            total_text += page.get_text()
        print('table of content Not found')
        total_text_lower = total_text.lower()

        # Find the start and end indices of the *headings*
        heading_boundaries = {} # {section_title: {'start': index, 'end': index}}

        # Search for each section in the specified order, starting the search
        # after the previous section was found.
        search_start_index = 0
        for section_title in SECTION_ORDER:
            if section_title not in SECTION_PATTERNS:
                 print(f"Pattern for section '{section_title}' is missing in SECTION_PATTERNS. Cannot proceed.")
                 return {} # Critical error, cannot find the section pattern

            pattern = re.compile(SECTION_PATTERNS[section_title], re.IGNORECASE)
            match = pattern.search(total_text_lower, search_start_index)

            if match:
                heading_boundaries[section_title] = {'start': match.start(), 'end': match.end()}
                print(f"Found '{section_title}' from index {match.start()} to {match.end()}.")
                search_start_index = match.end() # Start next search after this heading ends
            else:
                print(f"Section '{section_title}' not found in the document or not in expected order after the previous section.")
                # If a required section is missing, we can't define the boundaries
                return {} # Cannot proceed if key sections are missing

        # Check if all expected section boundaries were found
        if len(heading_boundaries) != len(SECTION_ORDER):
            print("Not all required section headings were found. Cannot extract text between them.")
            return {} # Not all sections found

        # Extract the text between the section headings
        item1_end = heading_boundaries[SECTION_ORDER[0]]['end']
        item1a_start = heading_boundaries[SECTION_ORDER[1]]['start']
        item1a_end = heading_boundaries[SECTION_ORDER[1]]['end']
        item1b_start = heading_boundaries[SECTION_ORDER[2]]['start']

        # Extract text between Item 1 and Item 1A
        text_item1_to_1a = total_text[item1_end:item1a_start].strip()
        print(f"Extracted text from index {item1_end} to {item1a_start}.")

        # Extract text between Item 1A and Item 1B
        text_item1a_to_1b = total_text[item1a_end:item1b_start].strip()
        print(f"Extracted text from index {item1a_end} to {item1b_start}.")

        extracted_content = {
            "Text between Item 1 and 1A": text_item1_to_1a,
            "Text between Item 1A and 1B": text_item1a_to_1b,
        }

    except FileNotFoundError:
        print(f"PDF file not found at {pdf_path}")
    except Exception as e:
        print(f"An error occurred while processing {pdf_path}: {e}", exc_info=True)
    finally:
        if doc:
            doc.close() # Always close the document

    return extracted_content

# Example Usage (for testing this script directly)
if __name__ == "__main__":
    # Create a dummy PDF for testing or use a path to a real one
    # You can save the provided OCR text into a text file and then convert it to PDF using an online tool
    # or a library, or use a publicly available SEC filing PDF.
    # Ensure your test PDF actually contains these exact sections in the specified order.

    # Using the Agilent filing you provided OCR for (assuming you save the full text as a PDF)
    agilent_10k_path = '/home/ammar/Desktop/k10 filing/data/input/ABBV.pdf' # <-- **CHANGE THIS PATH**
    arr = os.listdir('/home/ammar/Desktop/k10 filing/data/input')
    arr.sort()
    for i in arr:
        agilent_10k_path = f'/home/ammar/Desktop/k10 filing/data/input/{i}' # <-- **CHANGE THIS PATH**
        extracted_blocks = extract_text_between_specific_sections(agilent_10k_path)
    exit()
    # Add a basic file existence check
    if os.path.exists(agilent_10k_path):
        extracted_blocks = extract_text_between_specific_sections(agilent_10k_path)

        if extracted_blocks:
            print("\n--- Extracted Text Blocks ---")
            for label, content in extracted_blocks.items():
                print(f"\n--- {label} ---")
                # Print first 500 characters + '...' if content is long
                print(content[:500] + "..." if len(content) > 500 else content)
            print("-----------------------------")
        else:
            print(f"Could not extract requested text blocks from {agilent_10k_path}")
    else:
        print(f"ERROR: Test PDF not found at {agilent_10k_path}. Please update the path.")