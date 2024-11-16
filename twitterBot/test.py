import random
from typing import Optional
import tweepy
from rpc import post_to_sc
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

def create_twitter_client():
    """
    Creates and returns an authenticated Twitter client
    """
    # Get credentials from environment variables and strip any whitespace
    api_key = os.getenv('API_KEY', '').strip()
    api_secret = os.getenv('API_SECRET', '').strip()
    access_token = os.getenv('ACCESS_TOKEN', '').strip()
    access_token_secret = os.getenv('ACCESS_TOKEN_SECRET', '').strip()

    # Verify all credentials are present and properly formatted
    if not all([api_key, api_secret, access_token, access_token_secret]):
        raise ValueError(
            "Missing Twitter credentials. Please check your .env file contains:\n"
            "API_KEY\nAPI_SECRET\nACCESS_TOKEN\nACCESS_TOKEN_SECRET"
        )

    try:
        # Create authentication handler
        auth = tweepy.OAuth1UserHandler(
            api_key, 
            api_secret,
            access_token, 
            access_token_secret
        )

        # Test the credentials
        api = tweepy.API(auth)
        api.verify_credentials()
        
        return api
    except tweepy.errors.Unauthorized:
        raise ValueError("Invalid Twitter credentials. Please check your .env file.")
    except Exception as e:
        raise ValueError(f"Error creating Twitter client: {str(e)}")



def tweet(proof_hash: Optional[str], mention_id: str) -> str:
    """
    Creates a tweet response based on verification status.
    
    Args:
        proof_hash: The proof hash if verified, None if not verified
        mention_id: The tweet ID to mention/reply to
        
    Returns:
        str: The formatted tweet text
    """

    fake_messages = [
        "🚨 SCAM ALERT: This trade's faker than monopoly money! 💸",
        "❌ Busted! This PnL couldn't fool a calculator. 📉",
        "🕵️‍♂️ We investigated, and it's a hard NOPE. 🚫",
        "😂 Fake trade alert—somebody call the SEC! 📞",
        "🔥 This trade's cooked, and not in a good way. 🧯",
        "😅 Nice try, but we see through the smoke and mirrors. 🪞",
        "💀 RIP to this fake trade—it's DOA. 🚑",
        "🤡 Clown move detected—this PnL is a circus. 🎪",
        "🛑 Halted: This trade's about as real as Bigfoot. 🦶",
        "😤 Fraud level: Over 9000. This trade's a joke! 🤬",
        "🤔 Fake it till you make it? Not here. 🚫",
        "🚨 Fraud detected—somebody call the blockchain police! 👮",
        "📉 This trade's got more red flags than a bullring. 🚩",
        "😬 Scammy vibes confirmed. Try harder next time! 🕵️",
        "💥 This PnL just imploded under scrutiny. BOOM! 💣",
        "❗ Faker than a $3 bill. Not today! 💵",
        "🎭 Scam revealed—this trade's all smoke and mirrors. 🔍",
        "📢 Fraudulent trade spotted—tell your friends. 🗣️",
        "🪤 Caught in 4K! This trade's a straight-up scam. 🎥",
    ]

    verified_messages = [
        "🚀 This trade checks out—moonshot confirmed! 🌕",
        "🤑 Trade verified—somebody's swimming in gains! 💸",
        "🎯 Bullseye! This trade's the real deal. 🐂",
        "💎 Hands confirmed—this trader's a diamond among us! ✨",
        "🏆 Verified! Somebody deserves a trophy for this one. 🏅",
        "📊 PnL verified and it's pure gold. 💰",
        "✅ This trade's so clean, it sparkles. ✨",
        "🌟 True story—this PnL passes the vibe check. 🙌",
        "🔥 Legit as they come! Somebody's on a heater! ♨️",
        "📈 This trade's climbing the charts, and it's all real. 🎤",
        "🎉 Big win verified—pop the champagne! 🍾",
        "💸 This trade's the truth and nothing but the truth. 📜",
        "📈 The math adds up—green candles all day! 🕯️",
        "⚡ Verified: This trade's electrifying and real. ⚡",
        "💪 Strong hands, strong gains. Verified PnL! 🧾",
        "🚀 Confirmed legit—straight to the moon! 🌌",
        "📜 PnL verified—honesty pays off! 💵",
        "🎯 Bull run verified—this one's the real McCoy. 🤝",
    ]

    try:
        tweet_text = ""
        if proof_hash:
            try:
                verification_url = post_to_sc(proof_hash)
                message = random.choice(verified_messages)
                tweet_text = f"@{mention_id} {message}\n\n🔍 Verify: {verification_url}"
            except FileNotFoundError:
                print("Warning: Contract ABI file not found. Using proof hash directly.")
                message = random.choice(verified_messages)
                tweet_text = f"@{mention_id} {message}\n\n🔍 Proof Hash: {proof_hash}"
        else:
            tweet_text = f"@{mention_id} {random.choice(fake_messages)}"
        
        if not test_mode:
            try:
                # Create Twitter client and post
                api = create_twitter_client()
                response = api.update_status(tweet_text)
                print(f"Tweet posted successfully with ID: {response.id}")
            except Exception as e:
                print(f"Error posting to Twitter: {e}")
                # Still return the tweet text even if posting failed
        
        return tweet_text
                
    except Exception as e:
            print(f"Error creating tweet: {e}")
            return f"@{mention_id} We encountered an issue processing this trade."



# Example usage:


# Example usage
if __name__ == "__main__":
    # First, test environment variables
    print("\nChecking Twitter credentials...")
    print(f"API_KEY: {'✅' if os.getenv('API_KEY') else '❌'}")
    print(f"API_SECRET: {'✅' if os.getenv('API_SECRET') else '❌'}")
    print(f"ACCESS_TOKEN: {'✅' if os.getenv('ACCESS_TOKEN') else '❌'}")
    print(f"ACCESS_TOKEN_SECRET: {'✅' if os.getenv('ACCESS_TOKEN_SECRET') else '❌'}")
    
    # Test tweet generation without posting
    print("\nTesting tweet generation (no posting):")
    proof_hash = "67abdd721024f0ff4e0b3f4c2fc13bc5bad42d0b7851d456d88d203d15aaa450"
    
    print("\nTesting verified tweet:")
    tweet_text = tweet(proof_hash, "ImTheBigP")
    print(tweet_text)

    print("\nTesting fake tweet:")
    tweet_text = tweet(None, "ImTheBigP")
    print(tweet_text)
    
    # Test actual Twitter API connection
    print("\nTesting Twitter API connection:")
    try:
        client = create_twitter_client()
        print("✅ Twitter client created successfully!")
    except Exception as e:
        print(f"❌ Error creating Twitter client: {e}")