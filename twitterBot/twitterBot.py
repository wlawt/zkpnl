import tweepy
import requests
import os
import random
import json
import time
from typing import List, Dict, Optional, Tuple
from openai import OpenAI
from datetime import datetime, timezone
from dotenv import load_dotenv
import logging


class MentionStreamListener(tweepy.StreamingClient):
    def __init__(self, bearer_token: str, bot_instance):
        super().__init__(bearer_token)
        self.bot = bot_instance
        self.bot_username = os.getenv('BOT_USERNAME', '').lower()
        
    def on_tweet(self, tweet):
        try:
            # Check if the tweet is a mention of our bot
            if any(mention['username'].lower() == self.bot_username 
                   for mention in tweet.data['entities']['mentions']):
                
                # Extract the original tweet ID that was quoted or replied to
                referenced_tweet_id = None
                if tweet.data.get('referenced_tweets'):
                    for ref_tweet in tweet.data['referenced_tweets']:
                        if ref_tweet['type'] in ['quoted', 'replied_to']:
                            referenced_tweet_id = ref_tweet['id']
                            break
                
                if referenced_tweet_id:
                    self.bot.process_tweet(referenced_tweet_id, tweet.id)
                else:
                    # If no reference tweet, reply saying we need a tweet to analyze
                    self.bot.tweet_with_help_message(tweet.id)
                    
        except Exception as e:
            logging.error(f"Error in stream listener: {str(e)}")
            
    def on_error(self, status):
        logging.error(f"Stream error: {status}")
        
    def on_connection_error(self):
        logging.error("Stream connection error")
        return True  # Keep the stream alive


class TwitterBot:
    def __init__(self):
        """Initialize Twitter bot with API credentials from environment"""
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            filename='twitter_bot.log'
        )
        
        load_dotenv()
        
        # Twitter API setup
        self.api_key = os.getenv('API_KEY')
        self.api_secret = os.getenv('API_SECRET')
        self.access_token = os.getenv('ACCESS_TOKEN')
        self.access_token_secret = os.getenv('ACCESS_TOKEN_SECRET')
        self.bearer_token = os.getenv('BEARER_TOKEN')
        self.bot_username = os.getenv('BOT_USERNAME')
        
        if not all([self.api_key, self.api_secret, self.access_token, 
                   self.access_token_secret, self.bearer_token, self.bot_username]):
            raise ValueError("Missing Twitter API credentials in environment variables")
            
        auth = tweepy.OAuthHandler(self.api_key, self.api_secret)
        auth.set_access_token(self.access_token, self.access_token_secret)
        self.api = tweepy.API(auth)
        self.client = tweepy.Client(
            bearer_token=self.bearer_token,
            consumer_key=self.api_key,
            consumer_secret=self.api_secret,
            access_token=self.access_token,
            access_token_secret=self.access_token_secret
        )
        
        # Stream listener setup
        self.stream = MentionStreamListener(self.bearer_token, self)
        
        # OpenAI setup
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        if not self.openai_api_key:
            raise ValueError("Missing OpenAI API key in environment variables")
        
        self.openai_client = OpenAI(api_key=self.openai_api_key)
        
        # Create folders for images
        self.pnl_folder = "pnl"
        os.makedirs(self.pnl_folder, exist_ok=True)
        
        # Constants
        self.MAX_RETRIES = 3
        self.RETRY_DELAY = 2  # seconds
        
        logging.info("Bot initialized successfully")

    def start_mention_stream(self):
        """Start listening for mentions"""
        try:
            # Clear existing rules
            existing_rules = self.stream.get_rules()
            if existing_rules.data:
                rule_ids = [rule.id for rule in existing_rules.data]
                self.stream.delete_rules(rule_ids)
            
            # Add rule to track mentions
            self.stream.add_rules(tweepy.StreamRule(f"@{self.bot_username}"))
            
            # Start stream
            logging.info("Starting mention stream...")
            self.stream.filter(tweet_fields=['referenced_tweets', 'entities'])
            
        except Exception as e:
            logging.error(f"Error in mention stream: {str(e)}")
            # Attempt to restart stream after delay
            time.sleep(60)
            self.start_mention_stream()

    def tweet_with_help_message(self, reply_to_id: str) -> None:
        """Send help message when mentioned without a reference tweet"""
        help_messages = [
            "🤖 Hey there! To analyze a PnL, mention me in a reply to or quote tweet of the image you want to verify!",
            "👋 I'm here to help! Just mention me in a reply to the tweet containing the PnL screenshots you want to verify.",
            "💡 Quick tip: To use me, mention me while replying to or quoting a tweet with PnL screenshots!"
        ]
        self.tweet(random.choice(help_messages), reply_to_id)


    def download_image(self, image_url: str) -> str:
        """
        Download image from URL and save to PNL folder
        
        Args:
            image_url (str): URL of the image to download
            
        Returns:
            str: Path to saved image
        """
        try:
            response = requests.get(image_url, stream=True)
            if response.status_code == 200:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                extension = image_url.split('.')[-1].split('?')[0]
                filename = f"{timestamp}.{extension}"
                filepath = os.path.join(self.pnl_folder, filename)
                
                # Save image
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                return filepath
            else:
                print(f"Failed to download image from {image_url}")
        except Exception as e:
            print(f"Error downloading image: {str(e)}")

    def get_tweet_images(self, tweet_id: str) -> list:
        """
        Extract images from a tweet and save them
        
        Args:
            tweet_id (str): ID of the tweet to extract images from
            
        Returns:
            list: List of file paths to saved images
        """
        try:
            tweet = self.api.get_status(tweet_id, tweet_mode='extended')
            file_paths = []
            
            if hasattr(tweet, 'extended_entities') and 'media' in tweet.extended_entities:
                for media in tweet.extended_entities['media']:
                    if media['type'] == 'photo':
                        url = media['media_url']
                        local_path = self.download_image(url)
                        if local_path:
                            file_paths.append(local_path)
            return file_paths
        except Exception as e:
            print(f"Error getting tweet images: {str(e)}")
            return []

    def process_tweet(self, tweet_id: str) -> None:
        """
        Process a tweet to parse and save data for all images.

        Args:
            tweet_id (str): ID of the tweet to process
        """
        try:
            image_paths = self.get_tweet_images(tweet_id)
            parsed_data_files = []

            for image_path in image_paths:
                result = subprocess.run(
                    ["python", "image_parser.py", image_path],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    parsed_file_path = result.stdout.strip()
                    parsed_data_files.append(parsed_file_path)

            # Determine tweet response based on parsed data
            if not parsed_data_files:
                self.tweet_with_message("No valid data extracted from the images. 🚫 Try again!")
            else:
                verification_results = self.verify_parsed_data(parsed_data_files)
                self.respond_based_on_verification(verification_results, image_paths)

        except Exception as e:
            print(f"Error processing tweet {tweet_id}: {str(e)}")

    def verify_parsed_data(self, parsed_data_files: list) -> list:
        """
        Placeholder function to verify parsed data.

        Args:
            parsed_data_files (list): List of JSON file paths with parsed data
            
        Returns:
            list: List of verification results (True for valid, False for invalid)
        """
        # Replace with actual verification logic
        return [random.choice([True, False]) for _ in parsed_data_files]

    def respond_based_on_verification(self, results: list, image_paths: list) -> None:
        """
        Respond based on verification results.

        Args:
            results (list): List of verification results for each image
            image_paths (list): List of image paths
        """
        if all(results):
            self.tweet_with_verification_message(is_verified=True)
        elif any(results):
            self.tweet_with_partial_scam_message()
        else:
            self.tweet_with_verification_message(is_verified=False)

    def tweet_with_verification_message(self, is_verified: bool) -> None:
        """Post a tweet based on full verification results."""
        verified_messages = [
            "🚀 This trade checks out—moonshot confirmed! 🌕",
            "📈 100% legit—this trader’s cooking with gas! 🔥",
            "🤑 Trade verified—somebody’s swimming in gains! 💸",
            "🎯 Bullseye! This trade’s the real deal. 🐂",
            "💎 Hands confirmed—this trader’s a diamond among us! ✨",
            "🏆 Verified! Somebody deserves a trophy for this one. 🏅",
            "📊 PnL verified and it’s pure gold. 💰",
            "✅ This trade’s so clean, it sparkles. ✨",
            "🔍 Verified: This trade shines like a beacon of truth. 🛡️",
            "🌟 True story—this PnL passes the vibe check. 🙌",
            "🔥 Legit as they come! Somebody’s on a heater! ♨️",
            "📈 This trade’s climbing the charts, and it’s all real. 🎤",
            "🎉 Big win verified—pop the champagne! 🍾",
            "💸 This trade’s the truth and nothing but the truth. 📜",
            "📈 The math adds up—green candles all day! 🕯️",
            "⚡ Verified: This trade’s electrifying and real. ⚡",
            "💪 Strong hands, strong gains. Verified PnL! 🧾",
            "🚀 Confirmed legit—straight to the moon! 🌌",
            "📜 PnL verified—honesty pays off! 💵",
            "🎯 Bull run verified—this one’s the real McCoy. 🤝",
        ]

        fake_messages = [
            "🚨 SCAM ALERT: This trade’s faker than monopoly money! 💸",
            "❌ Busted! This PnL couldn’t fool a calculator. 📉",
            "🕵️‍♂️ We investigated, and it’s a hard NOPE. 🚫",
            "😂 Fake trade alert—somebody call the SEC! 📞",
            "🔥 This trade’s cooked, and not in a good way. 🧯",
            "😅 Nice try, but we see through the smoke and mirrors. 🪞",
            "💀 RIP to this fake trade—it’s DOA. 🚑",
            "🤡 Clown move detected—this PnL is a circus. 🎪",
            "🛑 Halted: This trade’s about as real as Bigfoot. 🦶",
            "😤 Fraud level: Over 9000. This trade’s a joke! 🤬",
            "🤔 Fake it till you make it? Not here. 🚫",
            "🚨 Fraud detected—somebody call the blockchain police! 👮",
            "📉 This trade’s got more red flags than a bullring. 🚩",
            "😬 Scammy vibes confirmed. Try harder next time! 🕵️",
            "💥 This PnL just imploded under scrutiny. BOOM! 💣",
            "❗ Faker than a $3 bill. Not today! 💵",
            "🎭 Scam revealed—this trade’s all smoke and mirrors. 🔍",
            "🤡 PnL verified as FAKE. Better luck next time. 🫠",
            "📢 Fraudulent trade spotted—tell your friends. 🗣️",
            "🪤 Caught in 4K! This trade’s a straight-up scam. 🎥",
        ]

        messages = verified_messages if is_verified else fake_messages
        message = random.choice(messages) + "\n Verify this for yourself on Zircuit!: " + "\n #Zircuit #Trading #Web3" #need function to grab zircuit link here and append to end 
        self.tweet(message)

    def tweet_with_partial_scam_message(self) -> None:
        """Post a tweet for partial scams."""
        mixed_messages = [
            "⚠️ Sneaky sneaky! Somebody tried to mix real trades with fake ones. 🚩",
            "🕵️ We caught a mix—some trades are real, but the fakes give it away. 🤡",
            "🤔 Nice try, but you can’t sneak fake trades past us! 🔍",
            "🚨 Partial scam alert—someone’s playing both sides! 🪤",
            "⚡ Some legit trades, but the fakes ruin the party. 🎭",
            "🔍 Caught in the act! Real trades don’t need fake backup. 🎬",
            "🧐 Mixing lies with truth doesn’t make it better. 🚫",
            "🤯 Half legit, half scam. Who are you trying to fool? 🙃",
            "😤 Almost had us, but fake trades don’t fly here. 🛫",
            "😂 A little truth can’t cover up a big lie! 🤥",
            "🚨 Mixed bag detected! Be better, scammers. 🛑",
            "🪞 Truth mixed with lies still breaks the mirror. 🔨",
            "🛠️ Fix your strategy—half scams aren’t better than full scams! 🧩",
            "🎭 Fake it all the way next time! This half-scam is embarrassing. 🤦",
            "🤖 Can’t fool us with a partial truth—our bot is smarter! 🛡️",
            "📊 Your numbers might match, but your integrity doesn’t. 💔",
            "🚫 Real PnLs don’t hide behind fake trades! 🎭",
            "⚠️ Fake friends alert—your PnLs need better company. 🚩",
            "🧨 Fake trades blow up the whole thing. Be real next time. 💥",
            "🥇 Real trades don’t need to be propped up by scams. 🎯",
        ]
        self.tweet(random.choice(mixed_messages))

    def tweet(self, text: str) -> None:
        """Post a tweet."""
        try:
            self.client.create_tweet(text=text)
        except Exception as e:
            print(f"Error posting tweet: {str(e)}")


def run_bot():
    """Main function to run the bot"""
    while True:
        try:
            logging.info("Initializing bot...")
            bot = TwitterAnalyzerBot()
            
            logging.info("Starting mention stream...")
            bot.start_mention_stream()
            
        except Exception as e:
            logging.error(f"Critical error: {str(e)}")
            logging.info("Restarting bot in 60 seconds...")
            time.sleep(60)

if __name__ == "__main__":
    run_bot()
