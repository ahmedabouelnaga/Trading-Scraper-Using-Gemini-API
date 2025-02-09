from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import re
import threading
import time
import json
from typing import List, Dict, Optional, Union, Any
from datetime import datetime, timedelta
import os
from threading import Lock
import pytz
import schedule
import sys
import logging
from logging import handlers
import signal
import traceback
from pathlib import Path
import google.generativeai as genai
from google.api_core import retry
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
HEADLESS_MODE = True
WAIT_TIMEOUT = 10
MAX_THREADS = 5
THREAD_TIMEOUT = 300
OUTPUT_FILE = "congress_trades.json"
RUNNING = True  # Global flag for graceful shutdown

# Get API key from environment variable
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    logger.critical("GEMINI_API_KEY not found in environment variables")
    sys.exit(1)

# Initialize Gemini
try:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-pro')
except Exception as e:
    logger.critical(f"Failed to initialize Gemini API: {str(e)}")
    sys.exit(1)

# Setup logging with rotation
log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
log_handler = logging.handlers.RotatingFileHandler(
    'trades_analyzer.log',
    maxBytes=10_000_000,  # 10MB
    backupCount=5
)
log_handler.setFormatter(log_formatter)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(log_formatter)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(log_handler)
logger.addHandler(console_handler)

# Create a lock for thread-safe file writing
file_lock = Lock()

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    global RUNNING
    logger.info("Shutdown signal received. Waiting for current tasks to complete...")
    RUNNING = False

# Register signal handlers
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def get_current_time_est() -> datetime:
    """Get current time in EST/EDT."""
    est = pytz.timezone('America/New_York')
    return datetime.now(est)

def get_timestamp_str() -> str:
    """Get formatted timestamp string."""
    current_time = get_current_time_est()
    return current_time.strftime("%A, %B %d, %Y %I:%M:%S %p %Z")

def initialize_json_file() -> None:
    """Initialize JSON file if it doesn't exist."""
    if not os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, 'w') as f:
            json.dump({
                "trading_sessions": []
            }, f, indent=2)

def write_to_json_file(data: Dict[str, Any]) -> None:
    """Write data to JSON file in a thread-safe manner."""
    with file_lock:
        try:
            # Read existing data
            with open(OUTPUT_FILE, 'r') as f:
                file_data = json.load(f)

            # Find or create today's trading session
            current_time = get_current_time_est()
            session_date = current_time.strftime("%Y-%m-%d")
            
            # Look for existing session for today
            session_found = False
            for session in file_data["trading_sessions"]:
                if session["date"] == session_date:
                    session["analyses"].append(data)
                    session_found = True
                    break
            
            # Create new session if none exists for today
            if not session_found:
                new_session = {
                    "date": session_date,
                    "market_open_time": get_timestamp_str(),
                    "analyses": [data]
                }
                file_data["trading_sessions"].append(new_session)
            
            # Write updated data back to file
            with open(OUTPUT_FILE, 'w') as f:
                json.dump(file_data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error writing to JSON file: {str(e)}")
            logger.error(traceback.format_exc())

def get_congress_member_tweets(username: str) -> List[tuple]:
    """Fetch tweets for a given congressional member."""
    options = webdriver.FirefoxOptions()
    if HEADLESS_MODE:
        options.add_argument('--headless')
    driver = webdriver.Firefox(options=options)
    tweets = []
    
    try:
        driver.get(f"https://twitter.com/{username}")
        wait = WebDriverWait(driver, WAIT_TIMEOUT)
        
        tweet_elements = wait.until(EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, '[data-testid="tweet"]')
        ))
        
        for tweet in tweet_elements:
            try:
                tweet_text = tweet.find_element(By.CSS_SELECTOR, '[data-testid="tweetText"]').text
                tweets.append((username, tweet_text))
            except NoSuchElementException:
                continue
                
        return tweets
    except (NoSuchElementException, TimeoutException) as e:
        logger.error(f"Error fetching tweets for {username}: {str(e)}")
        logger.error(traceback.format_exc())
        return []
    finally:
        driver.quit()

def validate_api_key():
    """Validate the Gemini API key."""
    try:
        response = model.generate_content("Test")
        return True
    except Exception as e:
        logger.critical(f"Invalid Gemini API key: {str(e)}")
        return False

@retry.Retry(predicate=retry.if_exception_type(Exception))
def analyze_tweet(username: str, text: str) -> Optional[Dict[str, Union[str, int]]]:
    """
    Analyze tweet content using Gemini to extract trading information.
    Returns structured data about congressional trades.
    """
    if not text:
        return None
    
    try:
        prompt = f"""
        You are a professional financial analyst specializing in congressional trading patterns and market sentiment analysis. Analyze the following tweet with high precision and strict adherence to guidelines.

        TWEET FOR ANALYSIS:
        From Congressional Member: {username}
        Content: {text}

        ANALYSIS REQUIREMENTS:
        1. Trading Activity Indicators:
           BULLISH Signals (indicating buying/positive sentiment):
           - Direct purchases or acquisitions
           - Opening new long positions
           - Call options purchases
           - Position increases
           - Accumulation language
           - Terms: buy, acquire, long, accumulate, increase position

           BEARISH Signals (indicating selling/negative sentiment):
           - Direct sales or disposals
           - Opening short positions
           - Put options purchases
           - Position decreases
           - Liquidation language
           - Terms: sell, dispose, short, reduce, liquidate

        2. Stock Symbol Requirements:
           - Must be prefixed with $
           - Verify symbol against common stock tickers
           - Ignore non-standard or unclear symbols

        3. Trade Magnitude Scale (1-10):
           10: Major portfolio changes (>$1M or >50% position)
           9: Very large strategic trades
           8: Significant position changes
           7: Notable strategic adjustments
           6: Moderate position changes
           5: Average-sized trades
           4: Small but meaningful trades
           3: Minor position adjustments
           2: Very small trades
           1: Minimal position changes

        4. Confidence Requirements:
           - Only return results for high-confidence matches
           - Must identify clear trading intent
           - Require explicit stock symbols
           - Verify congressional member context

        OUTPUT REQUIREMENTS:
        Respond ONLY with a valid JSON object containing these exact fields:
        {{
            "member_name": string (full name if known, otherwise Twitter handle),
            "company_traded": string (stock symbol with $ prefix),
            "trade_direction": string (exactly "good" for bullish or "bad" for bearish),
            "trade_magnitude": integer (1-10 scale based on criteria above),
            "tweet_text": string (original tweet text)
        }}

        If ANY of these conditions are not met, respond with "null":
        - No clear trading activity detected
        - Missing or unclear stock symbol
        - Ambiguous trading direction
        - Low confidence in interpretation
        - Cannot verify congressional connection

        ADDITIONAL CONTEXT:
        - Consider timing words ("just", "recently", "today")
        - Look for position size indicators
        - Account for market context if mentioned
        - Consider regulatory filing mentions
        - Check for related family member trades
        """

        # Add safety check for content
        response = model.generate_content(prompt)
        
        if not response.text:
            return None
            
        try:
            result = json.loads(response.text.strip())
            if result:
                result['tweet_text'] = text
                result['timestamp'] = get_timestamp_str()
            return result
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON response from Gemini: {response.text}")
            return None
            
    except Exception as e:
        logger.error(f"Error analyzing tweet: {str(e)}")
        logger.error(traceback.format_exc())
        return None

def process_tweet(username: str, text: str) -> None:
    """Process a single tweet and write the analysis results to JSON file."""
    if not text:
        return
        
    stock_symbols = re.findall(r'\$([A-Z]+)', text)
    
    if not stock_symbols:
        return
    
    analysis = analyze_tweet(username, text)
    
    if analysis:
        write_to_json_file(analysis)
        logger.info(f"Processed tweet from {username}: {text[:100]}...")

def run_analysis() -> None:
    """Main analysis function that runs at market open."""
    if not validate_api_key():
        logger.error("Invalid API key. Skipping analysis.")
        return

    try:
        logger.info(f"Starting analysis at {get_timestamp_str()}")
        
        # Read Twitter handles
        with open("twitter_handles.txt", "r") as f:
            twitter_handles = [line.strip() for line in f.readlines() if line.strip()]
        
        if not twitter_handles:
            raise ValueError("No Twitter handles found in file")
        
        def process_tweets(handles: List[str]) -> None:
            for handle in handles:
                try:
                    tweets = get_congress_member_tweets(handle)
                    for username, tweet in tweets:
                        process_tweet(username, tweet)
                except Exception as e:
                    logger.error(f"Error processing handle {handle}: {str(e)}")
                    logger.error(traceback.format_exc())
                    continue
        
        # Split handles among threads
        num_threads = min(MAX_THREADS, len(twitter_handles))
        handles_per_thread = len(twitter_handles) // num_threads
        thread_handles = [
            twitter_handles[i:i + handles_per_thread]
            for i in range(0, len(twitter_handles), handles_per_thread)
        ]
        
        # Start threads
        threads = []
        for handle_group in thread_handles:
            thread = threading.Thread(target=process_tweets, args=(handle_group,))
            thread.daemon = True
            threads.append(thread)
            thread.start()
        
        # Wait for threads to complete
        for thread in threads:
            thread.join(timeout=THREAD_TIMEOUT)
            
        logger.info(f"Analysis complete at {get_timestamp_str()}")
            
    except Exception as e:
        logger.error(f"Fatal error in analysis: {str(e)}")
        logger.error(traceback.format_exc())

def restart_program():
    """Restart the entire program."""
    logger.info("Restarting program...")
    try:
        os.execv(sys.executable, ['python'] + sys.argv)
    except Exception as e:
        logger.error(f"Failed to restart: {str(e)}")
        sys.exit(1)

def schedule_market_open() -> None:
    """Schedule the script to run at market open (9:30 AM EST) and keep running indefinitely."""
    global RUNNING
    
    # Initialize JSON file
    initialize_json_file()
    
    # PRODUCTION MODE: Uncomment these for normal operation
    # schedule.every().monday.at("09:30").do(run_analysis)
    # schedule.every().tuesday.at("09:30").do(run_analysis)
    # schedule.every().wednesday.at("09:30").do(run_analysis)
    # schedule.every().thursday.at("09:30").do(run_analysis)
    # schedule.every().friday.at("09:30").do(run_analysis)
    
    # TEST MODE: Uncomment this line to run immediately and test the scraper
    run_analysis()  # This will run once immediately
    
    # Heartbeat logger
    schedule.every().hour.do(lambda: logger.info("Scheduler heartbeat - still running"))
    
    logger.info(f"Scheduler initialized at {get_timestamp_str()}")
    if not any(job.job_func.__name__ == 'run_analysis' for job in schedule.jobs):
        logger.warning("Running in TEST MODE - Will run once immediately")
    else:
        logger.info("Waiting for next market open. Will run automatically at 9:30 AM EST on weekdays.")

    consecutive_errors = 0
    
    while RUNNING:
        try:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
            consecutive_errors = 0  # Reset error count on successful iteration
            
        except Exception as e:
            consecutive_errors += 1
            logger.error(f"Error in main loop: {str(e)}")
            logger.error(traceback.format_exc())
            
            if consecutive_errors >= 5:
                logger.critical("Too many consecutive errors. Attempting restart...")
                restart_program()
            
            # Wait before retrying
            time.sleep(60)

def create_daemon():
    """Run the program as a daemon process."""
    try:
        # Create a new session ID for the daemon process
        if os.name != 'nt':  # Not on Windows
            pid = os.fork()
            if pid > 0:
                sys.exit(0)  # Exit first parent
                
            os.setsid()
            
            pid = os.fork()
            if pid > 0:
                sys.exit(0)  # Exit second parent
            
            # Close file descriptors
            for fd in range(0, 3):
                try:
                    os.close(fd)
                except OSError:
                    pass
                    
            # Redirect standard file descriptors
            sys.stdout.flush()
            sys.stderr.flush()
            
            with open(os.devnull, 'r') as f:
                os.dup2(f.fileno(), sys.stdin.fileno())
            with open('stdout.log', 'a+') as f:
                os.dup2(f.fileno(), sys.stdout.fileno())
            with open('stderr.log', 'a+') as f:
                os.dup2(f.fileno(), sys.stderr.fileno())
    
    except Exception as e:
        logger.error(f"Failed to daemonize: {str(e)}")
        logger.error(traceback.format_exc())
        return False
        
    return True

if __name__ == "__main__":
    try:
        # Run as daemon on Unix-like systems
        if os.name != 'nt':
            if not create_daemon():
                logger.error("Failed to create daemon. Running in foreground.")
        
        logger.info("Starting Congressional Trade Analyzer...")
        logger.info(f"Process ID: {os.getpid()}")
        logger.info(f"Started at: {get_timestamp_str()}")
        
        # Start the scheduler
        schedule_market_open()
        
    except Exception as e:
        logger.critical(f"Fatal error: {str(e)}")
        logger.critical(traceback.format_exc())
        sys.exit(1)