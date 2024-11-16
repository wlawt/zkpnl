import os
import requests
import json
from typing import List, Dict
import shutil
from dotenv import load_dotenv
import base64
from openai import OpenAI
import tweepy
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

load_dotenv()

def create_twitter_client():
    """
    Creates a Twitter client with rate limit handling
    """
    return tweepy.Client(
        bearer_token=os.getenv('BEARER_TOKEN'),
        wait_on_rate_limit=True  # This makes tweepy automatically wait when we hit rate limits
    )

def get_img_from_tweet(mention_tweet_id: str, save_folder: str = "pnl", max_retries: int = 3) -> bool:
    """
    Downloads images from a tweet that mentions the bot with rate limit handling.
    
    Args:
        mention_tweet_id: ID of the tweet that mentions the bot
        save_folder: Folder to save images (default: "pnl")
        max_retries: Maximum number of retries for rate limits
    
    Returns:
        bool: True if images were downloaded successfully
    """
    try:
        # Get the absolute path of the script directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # Create the full path for the save folder
        save_folder_path = os.path.join(script_dir, save_folder)
        
        print(f"Current working directory: {os.getcwd()}")
        print(f"Save folder path: {save_folder_path}")
        
        # Ensure the save folder exists
        os.makedirs(save_folder_path, exist_ok=True)
        
        # Create session with retry strategy for downloading images
        session = requests.Session()
        retries = Retry(
            total=max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        session.mount('https://', HTTPAdapter(max_retries=retries))
        
        # Initialize Twitter client with rate limit handling
        client = create_twitter_client()
        
        # Get tweet data with retry logic
        for attempt in range(max_retries):
            try:
                tweet = client.get_tweet(
                    mention_tweet_id,
                    expansions=['attachments.media_keys'],
                    media_fields=['url', 'preview_image_url', 'type']
                )
                break
            except tweepy.errors.TooManyRequests as e:
                if attempt == max_retries - 1:
                    print(f"Final retry failed. Error: {str(e)}")
                    return False
                wait_time = 2 ** attempt  # Exponential backoff
                print(f"Rate limit hit. Waiting {wait_time} seconds before retry...")
                time.sleep(wait_time)
            except Exception as e:
                print(f"Error getting tweet: {str(e)}")
                return False
        
        if not tweet.includes or 'media' not in tweet.includes:
            print("No media found in mention tweet")
            return False
        
        # Get media URLs
        media_files = []
        for media in tweet.includes['media']:
            if hasattr(media, 'url'):
                media_files.append(media.url)
            elif hasattr(media, 'preview_image_url'):
                media_files.append(media.preview_image_url)
        
        if not media_files:
            print("No valid media URLs found")
            return False
        
        print(f"Found {len(media_files)} media files")
        
        # Download images with retry session
        for idx, media_url in enumerate(media_files, 1):
            print(f"Downloading media from: {media_url}")
            try:
                response = session.get(media_url, timeout=10)
                response.raise_for_status()
                
                file_path = os.path.join(save_folder_path, f"{idx}.png")
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                
                if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                    print(f"Successfully saved image {idx} to {file_path}")
                    print(f"File size: {os.path.getsize(file_path)} bytes")
                else:
                    print(f"Failed to save image or file is empty: {file_path}")
                    
            except requests.exceptions.RequestException as e:
                print(f"Error downloading image {idx}: {str(e)}")
                continue
        
        # Verify downloads
        saved_files = [f for f in os.listdir(save_folder_path) if f.endswith('.png')]
        print(f"\nSuccessfully downloaded {len(saved_files)} of {len(media_files)} images")
        
        return len(saved_files) > 0
        
    except Exception as e:
        print(f"Error in get_img_from_tweet: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return False

def get_data_from_ai(folder_path: str = "pnl") -> List[Dict]:
    """
    Processes images using OpenAI API and returns trading data.
    Deletes images after successful processing.
    """
    try:
        results = []
        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        # Get all image files
        image_files = sorted([f for f in os.listdir(folder_path) if f.endswith(('.png', '.jpg', '.jpeg'))])
        
        for image_file in image_files:
            image_path = os.path.join(folder_path, image_file)
            
            # Read and encode image
            with open(image_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')
            
            # Prepare the prompt for OpenAI
            prompt = """Analyze this trading chart image and extract the following information in JSON format only:
            - entry price
            - exit price
            - percentage gain/loss
            - leverage
            
            Return ONLY the JSON object with these fields, nothing else. Example format:
            {"entry": 100.5, "exit": 120.3, "percentage": 19.7, "leverage": 80}
            
            REMEBER : if you dont see any long postion with leverage 80X then we put in the value of 80 otherwise just use 1 if leverage is not used.
            """
            
            # Call OpenAI API
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=300
            )
            
            # Parse the response into JSON
            try:
                trade_data = json.loads(response.choices[0].message.content)
                results.append(trade_data)
            except json.JSONDecodeError:
                print(f"Error parsing JSON for image {image_file}")
                continue
        
        # If all images processed successfully, delete them
        if len(results) == len(image_files):
            shutil.rmtree(folder_path)
            os.makedirs(folder_path)
        
        return results
    except Exception as e:
        print(f"Error processing images: {str(e)}")
        return []
    


get_img_from_tweet("1857741559158219055") 