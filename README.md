# CapCheck: Telegram Bot for Verifying Trading PnL Claims

CapCheck is an interactive Telegram bot designed to combat fraudulent trading profit-and-loss (PnL) claims and promote transparency in trading communities. Fraudulent actors often use platforms like Telegram to share doctored PnL images, pretending to be profitable traders. These “crypto gurus” post impossible percent returns to entice amateur traders into following their fraudulent courses or schemes. At the same time, genuine traders showing off real successes often face unwarranted skepticism because of the bad reputation created by these scams.

## Why Telegram?
We chose Telegram as our primary platform because it is the hub of many trading communities and where a significant portion of these grifts occur. Many people in this space spend a large part of their time on Telegram, making it the ideal platform for CapCheck to interact with its audience. However, CapCheck also supports images originating from other sources, such as Twitter screenshots, ensuring accessibility across platforms.

## How It Works
1. **Upload PnL Images**  
   Users upload PnL images to CapCheck’s Telegram bot. Whether the image originates from Telegram, Twitter, or elsewhere, the bot processes it seamlessly.

2. **AI-Powered Image Parsing**  
   CapCheck leverages OpenAI’s GPT-based API to extract critical details from the uploaded images, including:  
   - Entry price  
   - Current price  
   - Percentage gain/loss  

   Preprocessing techniques like format normalization and content enhancement ensure consistent and accurate data extraction across various image types.

3. **Cross-Referencing Data**  
   The extracted PnL data is cross-referenced with real trade data from Binance's open ledger or other public blockchain data. Our system uses a bi-pronged approach:  
   - Matching the price claims to historical ledger data  
   - Calculating percentage returns externally and verifying against the claims  

   This ensures that the verification process remains both robust and accurate.

4. **Zero-Knowledge Proof Validation**  
   The verified data is fed into a zero-knowledge proof system implemented using the RISC Zero ZKVM. The ZKVM securely executes the PnL calculation formula:  
   `pnl = ((current - entry) / entry) * 100`  

   If the provided data matches the calculated values, the ZKVM generates a proof hash, ensuring that the process remains trustless and secure. This proof is cryptographically verifiable without exposing sensitive trade details.

5. **Feedback and Transparency**  
   Once the data has been processed, CapCheck provides feedback directly through the Telegram bot:  
   - Categorizing the PnL as **verified**, **fake**, or **mixed** (partially fake).  
   - Sharing the relevant ZK proof hash for transparency and public accountability.  

   CapCheck automates this entire workflow to provide real-time responses, helping traders identify scams and validate genuine claims.

## Why Use CapCheck?
- **Transparency:** CapCheck makes it easy for anyone to verify the authenticity of trading claims.  
- **Trustless Validation:** With ZK-proof technology, verification is both secure and cryptographically trustless.  
- **Designed for the Community:** Built specifically for Telegram, where many trading communities and scams originate.  
- **Platform Agnostic:** Works with PnL images from Telegram, Twitter, and other sources.

## Key Features
- AI-driven image processing powered by OpenAI API  
- Zero-knowledge proof validation using RISC Zero ZKVM  
- Integration with Binance's open ledger for trade verification  
- Telegram bot interface for easy and intuitive user interaction  
- Transparent feedback with proof hashes stored on the Zircuit Testnet  

CapCheck promotes accountability in trading communities, helping eliminate fraudulent practices while empowering genuine traders to share their verified successes.  
