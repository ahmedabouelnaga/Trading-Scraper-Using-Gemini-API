# Congressional Trade Analyzer
A tool for analyzing congressional trading activity from Twitter using Google's Gemini AI.
## ⚠️ Disclaimer
This project is for **educational purposes only**. The author:
- Takes no responsibility for how others use this code
- Does not endorse or encourage excessive scraping or DOS attacks
- Provides this as a learning exercise for understanding web scraping, API integration, and data analysis
- Recommends reviewing and respecting Twitter's Terms of Service and rate limits
- Makes no guarantees about the accuracy of the AI analysis

## 🎯 Overview
This script monitors Twitter for congressional trading activity, analyzes tweets using Google's Gemini AI, and logs trading patterns. It runs automatically during market hours and handles data collection safely and efficiently.

## 📥 Getting Started
1. Clone the repository:
```bash
git clone https://github.com/ahmedabouelnaga/Trade-Scraper-Using-Gemini-API.git
cd Trade-Scraper-Using-Gemini-API
```

2. Create and activate a virtual environment (recommended):
```bash
# On Unix/macOS
python -m venv venv
source venv/bin/activate

# On Windows
python -m venv venv
.\venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## 🚀 Setup & Installation

### Prerequisites
```bash
pip install -r requirements.txt
```

Required packages:
- selenium
- python-dotenv
- google-generativeai
- schedule
- pytz
- ratelimit
- google-api-core

### Configuration
1. Create a .env file in the project root:
```
GEMINI_API_KEY=your_gemini_api_key_here
```

2. Create twitter_handles.txt with Twitter handles to monitor:
```
@handle1
@handle2
```
3. Install Firefox (required for Selenium)

## 🧪 Testing the Script
### Test Mode
To test outside market hours:
1. Open `trades_analyzer.py`
2. Locate the `schedule_market_open()` function
3. Comment out the production schedules and enable test mode:
```python
# PRODUCTION MODE - Comment these for testing:
# schedule.every().monday.at("09:30").do(run_analysis)
# schedule.every().tuesday.at("09:30").do(run_analysis)
# schedule.every().wednesday.at("09:30").do(run_analysis)
# schedule.every().thursday.at("09:30").do(run_analysis)
# schedule.every().friday.at("09:30").do(run_analysis)

# TEST MODE - Uncomment this:
run_analysis()  # Runs immediately once
```

### Reverting to Production Mode
1. Re-comment the test line
2. Uncomment the schedule lines:
```python
# PRODUCTION MODE - Uncomment these:
schedule.every().monday.at("09:30").do(run_analysis)
schedule.every().tuesday.at("09:30").do(run_analysis)
schedule.every().wednesday.at("09:30").do(run_analysis)
schedule.every().thursday.at("09:30").do(run_analysis)
schedule.every().friday.at("09:30").do(run_analysis)

# TEST MODE - Comment this:
# run_analysis()
```

## 🔧 Usage

### Starting the Script
```bash
python trades_analyzer.py
```

The script will:
- Run as a daemon process on Unix systems
- Schedule analysis for market hours (9:30 AM EST on weekdays)
- Log activities to trades_analyzer.log
- Store results in congress_trades.json

### Stopping the Script
- Press Ctrl+C for graceful shutdown
- The script will complete current tasks before exiting
- For emergency stop: find PID in trades_analyzer.log and use `kill -9 PID`

## 📊 Output
Results are stored in congress_trades.json:
```json
{
  "trading_sessions": [
    {
      "date": "2024-01-01",
      "market_open_time": "Monday, January 1, 2024 09:30:00 AM EST",
      "analyses": [
        {
          "member_name": "CongressPerson",
          "company_traded": "$STOCK",
          "trade_direction": "good/bad",
          "trade_magnitude": 1-10,
          "tweet_text": "original tweet",
          "timestamp": "analysis time"
        }
      ]
    }
  ]
}
```

## 🔍 Features
- Multi-threaded tweet processing
- Automatic restart on critical errors
- Rate limiting and retry logic
- Daemon process support
- Rotating log files
- Thread-safe file operations
- EST/EDT timezone handling
- Graceful shutdown handling

## 📝 Logs
- Main log: trades_analyzer.log (rotates at 10MB)
- stdout.log: Standard output
- stderr.log: Error messages

## ⚙️ Advanced Configuration
Edit these variables in trades_analyzer.py:
```python
HEADLESS_MODE = True  # Run Firefox in headless mode
WAIT_TIMEOUT = 10     # Selenium wait timeout
MAX_THREADS = 5       # Maximum concurrent threads
THREAD_TIMEOUT = 300  # Thread completion timeout
```

## 🛠 Troubleshooting
1. Selenium issues:
   - Ensure Firefox is installed
   - Check geckodriver compatibility

2. API errors:
   - Verify GEMINI_API_KEY in .env
   - Check API quota limits

3. Process won't start:
   - Check log files for errors
   - Verify file permissions

## 📚 Security Notes
- Never commit .env file
- Monitor API usage
- Respect rate limits
- Review logs regularly
- Keep packages updated

## 🤝 Contributing
This is an educational project. While contributions are welcome, remember:
- Follow ethical scraping practices
- Respect API terms of service
- Add proper error handling
- Document changes thoroughly

## ⚖️ Legal
This tool is provided "as is" without warranty. Users are responsible for:
- Complying with API terms of service
- Respecting website scraping policies
- Following applicable laws and regulations
- Managing their own API keys and usage

## 🎯 Quick Test Mode
To test the scraper immediately without waiting for market hours:
1. Open trades_analyzer.py
2. Find the schedule_market_open() function
3. Comment out the market hour schedules and uncomment the test mode line:
```python
# Comment out these lines for testing:
# schedule.every().monday.at("09:30").do(run_analysis)
# ...market schedules...

# Uncomment this line for immediate testing:
run_analysis()  # This will run the analysis immediately
```

## 🛑 Script Control Guide
### Running the Script
The script is designed to run indefinitely and will:
- Auto-start at system boot (if configured as a service)
- Automatically handle errors and restart
- Log all activities for monitoring

### Stopping Methods
1. **Graceful Shutdown (Recommended)**
   ```bash
   # Find PID
   ps aux | grep trades_analyzer.py
   # OR
   cat trades_analyzer.log | grep "Process ID"
   
   # Stop gracefully
   kill <PID>
   ```
   - Allows current analysis to complete
   - Saves all data properly
   - Closes connections safely

2. **Emergency Stop**
   ```bash
   kill -9 <PID>
   ```
   ⚠️ Use only if graceful shutdown fails
   - May leave incomplete data
   - Doesn't close connections properly

### Monitoring
1. **Check Status**
   ```bash
   ps aux | grep trades_analyzer.py
   ```

2. **View Live Logs**
   ```bash
   tail -f trades_analyzer.log
   ```

3. **Check Health**
   - Look for hourly heartbeat messages
   - Monitor for error patterns
   - Check output file updates

### Automatic Restarts
The script will automatically:
- Restart after 5 consecutive errors
- Log all restart attempts
- Maintain operation state

## 📋 Dependencies Details
### Required System Components
- Firefox Browser
- Python 3.8+
- Unix-like system for daemon mode (optional)

### Python Package Versions
```
selenium>=4.0.0
python-dotenv>=0.19.0
google-generativeai>=0.3.0
schedule>=1.1.0
pytz>=2021.3
google-api-core>=2.0.0
```

## 🔧 Common Operations
### Updating Twitter Handles
1. Edit twitter_handles.txt
2. No restart needed - handles are read each market day

### Changing Market Hours
Modify schedule_market_open() in trades_analyzer.py:
```python
schedule.every().monday.at("10:30").do(run_analysis)  # Different time
schedule.every().tuesday.at("09:30").do(run_analysis)
```

# Detailed Code Block Explanation

## 1. Imports and Initial Setup
```python
from selenium import webdriver
from selenium.webdriver.common.by import By
# ... other imports ...
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
```
This section:
- Imports all necessary tools and libraries
- Loads secret information (like API keys) from a .env file

## 2. Configuration and API Setup
```python
# Configuration
HEADLESS_MODE = True
WAIT_TIMEOUT = 10
MAX_THREADS = 5
THREAD_TIMEOUT = 300
OUTPUT_FILE = "congress_trades.json"
RUNNING = True

# Get API key from environment variable
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
```
This part:
- Sets up basic settings for how the program runs
- Gets the Gemini AI API key from the environment
- Initializes the Gemini AI model for later use

## 3. Logging System Setup
```python
log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
log_handler = logging.handlers.RotatingFileHandler(
    'trades_analyzer.log',
    maxBytes=10_000_000,  # 10MB
    backupCount=5
)
```
This creates:
- A system to record everything the program does
- Logs that rotate when they get too big (10MB)
- Both console and file logging

## 4. Time Handling Functions
```python
def get_current_time_est() -> datetime:
    """Get current time in EST/EDT."""
    est = pytz.timezone('America/New_York')
    return datetime.now(est)

def get_timestamp_str() -> str:
    """Get formatted timestamp string."""
    current_time = get_current_time_est()
    return current_time.strftime("%A, %B %d, %Y %I:%M:%S %p %Z")
```
These functions:
- Handle time zones (specifically EST for stock market)
- Format dates and times nicely for logging

## 5. File Management Functions
```python
def initialize_json_file() -> None:
    """Initialize JSON file if it doesn't exist."""
    if not os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, 'w') as f:
            json.dump({
                "trading_sessions": []
            }, f, indent=2)
```
This part:
- Creates the output file if it doesn't exist
- Sets up the basic structure for storing trade data

## 6. Tweet Collection Function
```python
def get_congress_member_tweets(username: str) -> List[tuple]:
    """Fetch tweets for a given congressional member."""
    options = webdriver.FirefoxOptions()
    if HEADLESS_MODE:
        options.add_argument('--headless')
    driver = webdriver.Firefox(options=options)
    tweets = []
```
This function:
- Opens Firefox (invisibly)
- Goes to a Twitter profile
- Collects all visible tweets
- Returns them for analysis

## 7. Gemini AI Analysis Function
```python
@retry.Retry(predicate=retry.if_exception_type(Exception))
def analyze_tweet(username: str, text: str) -> Optional[Dict[str, Union[str, int]]]:
```
This is the core analysis function that:
- Takes a tweet
- Sends it to Gemini AI with specific instructions
- Gets back trading information
- Has an extensive prompt to guide the AI's analysis

## 8. Tweet Processing Function
```python
def process_tweet(username: str, text: str) -> None:
    """Process a single tweet and write the analysis results to JSON file."""
    if not text:
        return
        
    stock_symbols = re.findall(r'\$([A-Z]+)', text)
```
This function:
- Looks for stock symbols in tweets ($AAPL style)
- Sends tweets for analysis if they contain stocks
- Saves the results

## 9. Main Analysis Runner
```python
def run_analysis() -> None:
    """Main analysis function that runs at market open."""
    if not validate_api_key():
        logger.error("Invalid API key. Skipping analysis.")
        return
```
This coordinates everything:
- Checks if the API key is valid
- Reads the list of Twitter accounts
- Manages multiple threads for faster processing

## 10. Scheduling System
```python
def schedule_market_open() -> None:
    """Schedule the script to run at market open (9:30 AM EST)."""
    # PRODUCTION MODE: Uncomment these for normal operation
    # schedule.every().monday.at("09:30").do(run_analysis)
    # ...
    
    # TEST MODE: Uncomment this line to run immediately
    run_analysis()
```
This part:
- Has two modes: Test and Production
- Test mode runs immediately
- Production mode runs at market open each day

## 11. Background Process (Daemon) Setup
```python
def create_daemon():
    """Run the program as a daemon process."""
    try:
        if os.name != 'nt':  # Not on Windows
            pid = os.fork()
```
This function:
- Makes the program run in the background
- Works differently on Windows vs Unix systems
- Handles logging for background operation

## Main Differences from Previous Version:
1. Uses Gemini AI instead of OpenAI
2. Has more robust error handling
3. Includes API key validation
4. Has a more detailed analysis prompt
5. Includes test mode for immediate running
6. Better logging of errors and activities
