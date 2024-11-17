import os
import logging
from typing import List, Dict
import json
import base64
import asyncio
import random
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from openai import OpenAI
from dotenv import load_dotenv
from rpc import call_zk, post_to_sc



# Load environment variables
load_dotenv()

FAKE_MESSAGES = [
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

VERIFIED_MESSAGES = [
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

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    welcome_message = (
        "🚀 Yo fam, welcome to the No-Cap PNL Verifier! 💯\n\n"
        "Tired of fake flexes? Same here! Drop your PNL screenshots and I'll hit 'em "
        "with that ZK proof verification. No 🧢, just straight facts!\n\n"
        "Just send your screenshots and watch me expose the frauds or "
        "verify your wins! Let's keep it a hundred! 💪\n\n"
        "Hit /help if you're lost in the sauce! 🌊"
    )
    
    # Create pnl directory if it doesn't exist
    script_dir = os.path.dirname(os.path.abspath(__file__))
    pnl_folder = os.path.join(script_dir, "pnl")
    os.makedirs(pnl_folder, exist_ok=True)
    
    # Clear any existing images
    for file in os.listdir(pnl_folder):
        if file.endswith('.png'):
            os.remove(os.path.join(pnl_folder, file))
    
    await update.message.reply_text(welcome_message)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    help_text = (
        "🤖 No-Cap Zone: How To Use This Bot 💯\n\n"
        "Here's the deal fam:\n"
        "1. 📸 Take a clean shot of your PNL\n"
        "2. 📤 Send it here\n"
        "3. 🧮 Watch me cook with the verification\n\n"
        "Commands for the squad:\n"
        "/start - Reset everything, fresh start vibes\n"
        "/help - You're looking at it rn 😎\n\n"
        "Let's catch these fake flexers! 🕵️‍♂️"
    )
    await update.message.reply_text(help_text)

async def process_image(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Process images sent by users."""
    try:
        status_message = await update.message.reply_text("👀 Checking out that PNL, gimme a sec fam...")
        
        # Create pnl directory if it doesn't exist
        script_dir = os.path.dirname(os.path.abspath(__file__))
        pnl_folder = os.path.join(script_dir, "pnl")
        os.makedirs(pnl_folder, exist_ok=True)
        
        # Get the image file
        photo = update.message.photo[-1]  # Get highest quality photo
        image_file = await context.bot.get_file(photo.file_id)
        
        # Save image to pnl folder
        image_path = os.path.join(pnl_folder, "1.png")  # Always save as 1.png since we process one at a time
        await image_file.download_to_drive(image_path)
        
        logger.info(f"Saved image to {image_path}")
        await status_message.edit_text("🧠 Running the numbers through the verification machine...")
        
        # Process image and get trading data
        trade_data = await analyze_pnl_image(image_path)
        
        if not trade_data:
            await status_message.edit_text("❌ Ay yo, this screenshot ain't it chief! Make sure it's clear and shows the full trade. Try again! 🔄")
            return
        
        # Show extracted data with style
        data_message = (
            "📊 Aight, here's what I'm seeing:\n\n"
            f"Entry: ${trade_data['entry']} 💰\n"
            f"Exit: ${trade_data['exit']} 💸\n"
            f"Gains: {trade_data['percentage']}% 📈\n"
            f"Leverage: {trade_data['leverage']}x 🎯\n\n"
            "🔍 Running that ZK proof check, hold tight..."
        )
        await status_message.edit_text(data_message)
        await asyncio.sleep(2)
        # Verify the trade data
        try:
            proof_hash = call_zk(
                trade_data['entry'],
                trade_data['exit'],
                trade_data['percentage'],
                trade_data['leverage']
            )
            
            if proof_hash:
                # Post to blockchain and get link
                proof_link = post_to_sc(proof_hash)
                verified_msg = random.choice(VERIFIED_MESSAGES)
                
                success_message = (
                    f"{verified_msg}\n\n"
                    f"NO CAP 🫡\n\n"
                    f"🔗 Proof: {proof_link}\n\n"
                    "You know where to find me if you need more verification, homie! 😉"
                )
                await status_message.edit_text(success_message)
            
        except Exception as e:
            # When verification fails (including NoneType and panics)
            logger.error(f"Verification error: {str(e)}")
            fake_msg = random.choice(FAKE_MESSAGES)
            scam_message = (
                f"{fake_msg}\n\n"
                f"This is pure CAP! 🧢\n\n"
                f"Entry: ${trade_data['entry']} ❌\n"
                f"Exit: ${trade_data['exit']} ❌\n"
                f"Claimed Gains: {trade_data['percentage']}% 🧢\n\n"
                "Better luck next time fam! 😏"
            )
            await status_message.edit_text(scam_message)

        # Clean up image regardless of outcome
        try:
            os.remove(image_path)
            logger.info("Cleaned up processed image")
        except Exception as e:
            logger.error(f"Error cleaning up image: {str(e)}")
            
    except Exception as e:
        logger.error(f"Error processing image: {str(e)}")
        await update.message.reply_text("💀 Ayo something's not working right! Give it another shot! 🔄")

async def analyze_pnl_image(image_path: str) -> Dict:
    """Analyze PNL image using GPT-4 Vision API."""
    try:
        # Read the image file
        with open(image_path, "rb") as image_file:
            # Create base64 string
            image_bytes = image_file.read()
        
        prompt = """Analyze this trading chart image and extract the following information in JSON format only:
        - entry price
        - exit price
        - percentage gain/loss
        - leverage
        
        Return ONLY the JSON object with these fields, nothing else. Example format:
        {"entry": 100.5, "exit": 120.3, "percentage": 19.7, "leverage": 80}
        
        REMEMBER: if you dont see any long position with leverage 80X then we put in the value of 80 otherwise just use 1 if leverage is not used.
        """
        
        # Make the API call
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
                                "url": f"data:image/png;base64,{base64.b64encode(image_bytes).decode('utf-8')}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=300
        )
        
        # Process the response
        content = response.choices[0].message.content.strip()
        
        # Remove any markdown formatting
        content = content.replace('```json', '').replace('```', '').strip()
        
        # Parse JSON response
        trade_data = json.loads(content)
        logger.info(f"Successfully extracted trade data: {trade_data}")
        
        # Validate all required fields are present
        required_fields = ['entry', 'exit', 'percentage', 'leverage']
        if not all(field in trade_data for field in required_fields):
            logger.error("Missing required fields in trade data")
            return None
        
        return trade_data
        
    except Exception as e:
        logger.error(f"Error analyzing image: {str(e)}")
        return None

def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token
    application = Application.builder().token(os.getenv('TELEGRAM_BOT_TOKEN')).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.PHOTO, process_image))

    # Run the bot until the user presses Ctrl-C
    application.run_polling()

if __name__ == '__main__':
    main()