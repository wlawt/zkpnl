### ZKPnL

CapCheck is a Twitter bot designed to combat fraudulent trading rampant profit-and-loss (PnL) claims and promote transparency in the trading community. We’ve come across multiple accounts who on a daily basis that pretend to be profitable traders, posting engaging and often ridiculous images showcasing entry and current prices of memecoins and other assets they “invested” in. These users promote nearly impossible percent returns, and connivingly awe inspiring budding traders or amateur enthusiasts to follow their fraudulent courses, methods and teachings. As a result, we often see genuine people showing off their successes, who get shut down and cancelled online for the disengaging reputation that deceptive “crypto gurus” put upon them. Our bot is the solution.

Leveraging OpenAI powered image processing and X(twitter)’s own API, CapCheck parses tweets it has been called to, downloading, uploading and pulling data from the PnL images. Our verification algorithm is fed the entry and current price, as well as the percent return claims extracted from the tweet. 

Our Zero Knowledge proof algorithm deploys a bi-pronged approach, matching both the price claims on the Binance open ledger, as well as corresponding percent returns we calculate externally. We’ve specifically employed error handling contingencies to deal with multiple trades displaying values we want, using matching conditionals to find the relevant trade. It goes without saying that a ZK proof is not really a ZK proof without satisfying some vital conditions, and by having our bi-pronged approach we ensure that the passed values are honest, generating a true trustless verifiable proof.

## How It Works

Users @ bot on post of PnL screenshot. CapCheck uses AI to extract critical details, including:

- Entry price
- Current price
- Percentage gain/loss

Extracted data is cross-referenced with public blockchain or exchange data to validate trade's authenticity. ZK-proof mechanism ensures that the verification process remains secure and trustless.

Real-Time Twitter Interaction:
- Based on verification results, CapCheck:

Posts response under the original tweet, categorizing the trade as verified, fake, or a mix (partial scam).
Uses fun, engaging prompts (e.g., "Scam alert!" or "Moonshot confirmed!") to drive engagement and awareness.

## How We Built It

CapCheck is an end-to-end solution that leverages blockchain technology, AI-powered image processing, and zero-knowledge proofs (ZKPs) to automate the verification of trading profit-and-loss (PnL) claims shared on social media platforms like Twitter. The project combines multiple technologies to ensure a trustless, scalable, and accurate verification process.

## Core Components

1. Twitter Bot Integration  
The bot is built using Python and the Tweepy API to interact with Twitter users. It listens for mentions via the Twitter Streaming API, where users can tag the bot in replies or quote tweets containing PnL images. Upon detecting a valid request, the bot downloads the images and begins the verification process. The bot also dynamically parses references to ensure compatibility with a variety of tweet formats. 

The bot responds to verification results with engaging and predefined messages, categorizing the claims as verified, fake, or mixed. These interactions help raise awareness about fraudulent practices and encourage trust in verified data.

2. AI-Powered Image Parsing  
AI is used to extract critical data from PnL images, including entry price, current price, and percentage gain or loss. OpenAI’s GPT-based API processes the images, ensuring accurate data extraction even from non-standardized formats. To handle edge cases like noisy or low-resolution images, preprocessing techniques are applied, including format normalization and content enhancement. This allows for consistent and accurate data extraction across various image types.

3. Zero-Knowledge Proof Validation  
The extracted PnL data is validated using a zero-knowledge proof mechanism implemented with the RISC Zero ZKVM. The ZKVM securely executes the PnL calculation formula pnl = ((current - entry) / entry) * 100 and generates a proof hash if the provided data matches the calculated values. The ZKP ensures the validity of the verification without exposing sensitive details about the trade. The proof is generated in Rust and can be used to verify the data integrity in a trustless manner.

4. Blockchain Integration  
A Solidity smart contract deployed on the Zircuit Testnet manages proof hashes generated by the ZKVM. The ProofVerifier contract allows users to store and verify proof hashes securely on-chain, ensuring the immutability and transparency of the verification process. The contract supports querying of stored proofs, enabling anyone to independently confirm the authenticity of a PnL claim. Foundry is used to streamline the development, testing, and deployment of the contract.

5. End-to-End Workflow  
- The Twitter bot identifies and downloads images from tweets.  
- AI-powered parsing extracts PnL data from the images.  
- The ZK proof system validates the extracted data against the provided claims.  
- Validated proof hashes are posted to the blockchain.  
- The bot replies to the user with the verification results.  

The integration between these components ensures minimal latency while maintaining security and transparency. The pipeline handles multiple requests in parallel and is fully automated, providing an efficient and scalable solution for verifying trading claims.

6. Key Technologies and Tools  
- OpenAI API for AI-driven image parsing and data extraction.  
- RISC Zero ZKVM for secure and efficient zero-knowledge proof validation.  
- Solidity and Foundry for smart contract development and deployment.  
- Tweepy for building the Twitter bot interface.  
- Python for orchestrating the overall workflow, including image handling and backend integration.  
- Zircuit Testnet as the blockchain infrastructure for logging proof hashes.

