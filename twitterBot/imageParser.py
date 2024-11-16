import sys
import os
import openai
import json
from dotenv import load_dotenv
from PIL import Image
from PIL import UnidentifiedImageError

def parse_image_with_gpt(image_path: str) -> dict:
    """
    Parse the image to extract entry price, current price, and percentage change using GPT.

    Args:
        image_path (str): Path to the image file
        
    Returns:
        dict: Parsed data containing entry price, current price, and percentage change
    """
    try:
        # Open the image to verify it is a valid image file
        with Image.open(image_path) as img:
            img.verify()

        # Simulate the OCR process (you might need to add OCR here if you don't already have the text data)
        with open(image_path, "rb") as file:
            response = openai.Image.create_completion(
                model="gpt-4",
                files=[{"name": os.path.basename(image_path), "content": file}],
                prompt=(
                    "Extract the following information from the image:\n"
                    "1. Entry Price\n"
                    "2. Current Price\n"
                    "3. Percentage Change\n"
                    "Format the output as JSON: {entry_price, current_price, percentage_change}"
                ),
            )
            text_response = response['choices'][0]['text']
        
        # Convert the response to a dictionary
        parsed_data = eval(text_response)
        return parsed_data

    except UnidentifiedImageError:
        print(f"File {image_path} is not a valid image.")
        return {}
    except Exception as e:
        print(f"Error parsing image {image_path}: {str(e)}")
        return {}

def save_parsed_data(parsed_data: dict, image_path: str) -> str:
    """
    Save parsed data to a file in the parsed folder.
    
    Args:
        parsed_data (dict): Parsed data from the image
        image_path (str): Original image path
        
    Returns:
        str: Path to the saved parsed data file
    """
    try:
        base_name = os.path.splitext(os.path.basename(image_path))[0]
        output_path = os.path.join("parsed", f"{base_name}_parsed.json")
        os.makedirs("parsed", exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(parsed_data, f, indent=4)
        return output_path
    except Exception as e:
        print(f"Error saving parsed data for {image_path}: {str(e)}")
        return ""

if __name__ == "__main__":
    load_dotenv()
    openai.api_key = os.getenv("OPENAI_API_KEY")

    # Get image path from command-line arguments
    if len(sys.argv) < 2:
        print("Usage: python image_parser.py <image_path>")
        sys.exit(1)

    image_path = sys.argv[1]
    parsed_data = parse_image_with_gpt(image_path)
    if parsed_data:
        save_parsed_data(parsed_data, image_path)
