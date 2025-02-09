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


# Code Block Explanations

## 1. Imports and Configuration
```python
from selenium import webdriver
from selenium.webdriver.common.by import By
# ... other imports ...

# Configuration
OPENAI_API_KEY = "your-key-here"
HEADLESS_MODE = True
WAIT_TIMEOUT = 10
MAX_THREADS = 5
THREAD_TIMEOUT = 300
OUTPUT_FILE = "congress_trades.json"
RUNNING = True
```
This section:
- Imports all needed libraries (like tools in a toolbox)
- Sets up important variables that control how the program runs
- HEADLESS_MODE means Firefox runs invisibly
- WAIT_TIMEOUT is how long to wait for pages to load
- MAX_THREADS is how many Twitter accounts it can check at once

## 2. Logging Setup
```python
log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
log_handler = logging.handlers.RotatingFileHandler(
    'trades_analyzer.log',
    maxBytes=10_000_000,  # 10MB
    backupCount=5
)
```
This part:
- Sets up a system to keep track of what the program does
- Creates log files that record everything that happens
- Rotates logs when they get too big (10MB)
- Keeps 5 backup log files

## 3. Twitter Scraping Function
```python
def get_congress_member_tweets(username: str) -> List[tuple]:
    options = webdriver.FirefoxOptions()
    if HEADLESS_MODE:
        options.add_argument('--headless')
    driver = webdriver.Firefox(options=options)
    tweets = []
    
    try:
        driver.get(f"https://twitter.com/{username}")
        # ... rest of function ...
```
This function:
- Opens Firefox browser (invisibly)
- Goes to a specific Twitter profile
- Collects all tweets it can find
- Returns them as a list

## 4. Tweet Analysis Function
```python
def analyze_tweet(username: str, text: str) -> Optional[Dict[str, Union[str, int]]]:
    if not text:
        return None
    
    client = OpenAI(api_key=OPENAI_API_KEY)
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{
                "role": "system",
                "content": """... prompt ..."""
            }]
```
This function:
- Takes a tweet's text
- Sends it to GPT to analyze
- Looks for trading information
- Returns information about any trades mentioned

## 5. JSON File Handling
```python
def write_to_json_file(data: Dict[str, Any]) -> None:
    with file_lock:
        try:
            with open(OUTPUT_FILE, 'r') as f:
                file_data = json.load(f)
            # ... rest of function ...
```
This part:
- Safely saves trading information to a file
- Makes sure multiple parts of the program don't write at once
- Organizes data by trading sessions and dates

## 6. Main Analysis Runner
```python
def run_analysis() -> None:
    try:
        logger.info(f"Starting analysis at {get_timestamp_str()}")
        
        with open("twitter_handles.txt", "r") as f:
            twitter_handles = [line.strip() for line in f.readlines() if line.strip()]
```
This function:
- Reads the list of Twitter accounts to check
- Starts the whole process of collecting and analyzing tweets
- Uses multiple threads to check several accounts at once

## 7. Scheduling System
```python
def schedule_market_open() -> None:
    initialize_json_file()
    
    schedule.every().monday.at("09:30").do(run_analysis)
    schedule.every().tuesday.at("09:30").do(run_analysis)
    # ... more scheduling ...
```
This part:
- Sets up when the program should run
- Schedules it for every weekday at 9:30 AM EST
- Keeps track of any errors that happen

## 8. Background Process Setup
```python
def create_daemon():
    try:
        if os.name != 'nt':  # Not on Windows
            pid = os.fork()
            # ... rest of function ...
```
This function:
- Makes the program run in the background
- Sets up proper logging for background mode
- Works differently on Windows vs other systems

## 9. Main Program Entry
```python
if __name__ == "__main__":
    try:
        if os.name != 'nt':
            if not create_daemon():
                logger.error("Failed to create daemon. Running in foreground.")
        # ... rest of main ...
```
This section:
- Starts the whole program
- Tries to run as a background process
- Sets up error handling
- Begins the scheduling system






