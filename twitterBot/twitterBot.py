import tweepy
import requests
import os
from dotenv import load_dotenv
from typing import Optional, List
from datetime import datetime

class TwitterBot:
    def __init__(self, api_key: str, api_secret: str, access_token: str, access_token_secret: str):
        """Initialize Twitter bot with API credentials"""
        auth = tweepy.OAuthHandler(api_key, api_secret)
        auth.set_access_token(access_token, access_token_secret)
        self.api = tweepy.API(auth)
        self.client = tweepy.Client(
            consumer_key=api_key,
            consumer_secret=api_secret,
            access_token=access_token,
            access_token_secret=access_token_secret
        )
        
        # create pnl folder
        self.pnl_folder = "pnl"
        os.makedirs(self.pnl_folder, exist_ok=True)

    def download_image(self, image_url: str) -> Optional[str]:
        """
        Download image from URL and save to PNL folder
        
        Args:
            image_url (str): URL of the image to download
            
        Returns:
            Optional[str]: Path to saved image or None if download failed
        """
        try:
            response = requests.get(image_url, stream=True)
            if response.status_code == 200:
                # Create filename using timestamp and original extension
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                extension = image_url.split('.')[-1].split('?')[0]
                filename = f"{timestamp}.{extension}"
                filepath = os.path.join(self.pnl_folder, filename)
                
                # Save image
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                return filepath
            return None
        except Exception as e:
            print(f"Error downloading image: {str(e)}")
            return None

    def get_tweet_images(self, tweet_id: str) -> List[dict]:
        """
        Extract images from a tweet and save them
        
        Args:
            tweet_id (str): ID of the tweet to extract images from
            
        Returns:
            List[dict]: List of dicts containing image URLs and local paths
        """
        try:
            tweet = self.api.get_status(tweet_id, tweet_mode='extended')
            images = []
            
            if hasattr(tweet, 'extended_entities') and 'media' in tweet.extended_entities:
                for media in tweet.extended_entities['media']:
                    if media['type'] == 'photo':
                        url = media['media_url']
                        local_path = self.download_image(url)
                        if local_path:
                            images.append({
                                'url': url,
                                'local_path': local_path
                            })
            return images
        except Exception as e:
            print(f"Error getting tweet images: {str(e)}")
            return []

    def handle_mention(self, mention: tweepy.Tweet) -> None:
        """Handle mentions of the bot"""
        try:
            if 'verify' in mention.text.lower():
                if mention.in_reply_to_status_id:
                    images = self.get_tweet_images(mention.in_reply_to_status_id)
                    
                    if images:
                        # Create reply with both URLs and local paths
                        image_list = '\n'.join([
                            f"URL: {img['url']}\nSaved to: {img['local_path']}"
                            for img in images
                        ])
                        reply_text = f"Found and saved these images:\n{image_list}"
                    else:
                        reply_text = "No images found in the tweet."
                    
                    self.client.create_tweet(
                        text=reply_text,
                        in_reply_to_tweet_id=mention.id
                    )
        except Exception as e:
            print(f"Error handling mention: {str(e)}")

    def tweet(self, text: str, image_path: Optional[str] = None) -> bool:
        """Post a tweet with optional image"""
        try:
            if image_path:
                media = self.api.media_upload(image_path)
                self.client.create_tweet(text=text, media_ids=[media.media_id])
            else:
                self.client.create_tweet(text=text)
            return True
        except Exception as e:
            print(f"Error posting tweet: {str(e)}")
            return False


if __name__ == "__main__":

    
    load_dotenv()
    #testing 
    bot = TwitterBot(
        api_key=os.getenv('API_KEY'),
        api_secret=os.getenv('API_SECRET'),
        access_token=os.getenv('ACCESS_TOKEN'),
        access_token_secret=os.getenv('ACCESS_TOKEN_SECRET')
    )

    class MentionStream(tweepy.StreamingClient):
        def on_tweet(self, tweet):
            bot.handle_mention(tweet)
    
    stream = MentionStream("YOUR_BEARER_TOKEN")
    stream.filter(tweet_fields=["referenced_tweets"])

    