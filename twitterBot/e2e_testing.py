import os
import json
from typing import List, Dict
import shutil
from dotenv import load_dotenv
import base64
from openai import OpenAI


load_dotenv()

def get_data_from_ai(folder_path: str = "pnl") -> List[Dict]:
    """
    Processes images using OpenAI API and returns trading data.
    Uses base64 encoded image data directly instead of URLs.
    """
    try:
        # Get the absolute path of the script directory and folder
        script_dir = os.path.dirname(os.path.abspath(__file__))
        folder_path = os.path.join(script_dir, folder_path)
        
        results = []
        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        # Get all image files
        image_files = sorted([f for f in os.listdir(folder_path) if f.endswith(('.png', '.jpg', '.jpeg'))])
        print(f"Found {len(image_files)} images to process")
        
        for img_name in image_files:
            image_path = os.path.join(folder_path, img_name)
            print(f"Processing image: {image_path}")
            
            # Read image file
            with open(image_path, "rb") as img_file:
                image_data = img_file.read()
            
            # Prepare the prompt for OpenAI
            prompt = """Analyze this trading chart image and extract the following information in JSON format only:
            - entry price
            - exit price
            - percentage gain/loss
            - leverage
            
            Return ONLY the JSON object with these fields, nothing else. Example format:
            {"entry": 100.5, "exit": 120.3, "percentage": 19.7, "leverage": 80}
            
            REMEMBER: if you dont see any long position with leverage 80X then we put in the value of 80 otherwise just use 1 if leverage is not used.
            """
            
            # Call OpenAI API with direct base64 image data
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{base64.b64encode(image_data).decode('utf-8')}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=300
            )
            
            # Parse the response into JSON
            try:
                # Clean up the response content
                content = response.choices[0].message.content
                # Remove markdown formatting if present
                content = content.replace('```json', '').replace('```', '').strip()
                
                trade_data = json.loads(content)
                print(f"Successfully processed image. Data: {trade_data}")
                results.append(trade_data)
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON for image {img_name}: {e}")
                print(f"Raw response: {response.choices[0].message.content}")
                # Try to extract JSON from markdown format
                try:
                    content = response.choices[0].message.content
                    # Find the JSON part between the backticks
                    import re
                    json_match = re.search(r'{.*}', content, re.DOTALL)
                    if json_match:
                        trade_data = json.loads(json_match.group())
                        print(f"Successfully extracted JSON after cleanup. Data: {trade_data}")
                        results.append(trade_data)
                except Exception as e:
                    print(f"Failed to extract JSON after cleanup: {e}")
                    continue
        
        print(f"Successfully processed {len(results)} images")
        
        # Clean up the images folder if we got results
        if results:  # Changed condition to check if we have any results
            print("Cleaning up images folder...")
            for img_name in image_files:
                image_path = os.path.join(folder_path, img_name)
                try:
                    os.remove(image_path)
                    print(f"Deleted: {image_path}")
                except Exception as e:
                    print(f"Error deleting {image_path}: {e}")
            print("Cleanup completed")
        
        return results
    except Exception as e:
        print(f"Error processing images: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return []
    

print(get_data_from_ai())
