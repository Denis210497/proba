# Trading Journal Application

A professional trading journal application to track your trades, analyze performance, and manage your trading account.

## Features

- Track trades with detailed information
- Upload and view trade screenshots
- Calculate profit/loss automatically
- View trading statistics and performance charts
- Manage account balance
- Delete and edit trades
- Professional UI with modern theme

## Installation

1. Make sure you have Python 3.8 or higher installed on your system.

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

1. Open a terminal/command prompt
2. Navigate to the trading_journal_app directory
3. Run the application:
```bash
python trading_journal.py
```

## How to Use

1. **Setting Up Account Balance**
   - Go to the "Account Settings" tab
   - Enter your trading account balance
   - Click "Update Balance"

2. **Adding a New Trade**
   - Go to the "New Trade" tab
   - Fill in the trade details
   - Use the "Browse" button to add screenshots
   - Click "Save Trade"

3. **Viewing Trades**
   - Go to the "Trade List" tab
   - Double-click any trade to view details
   - Right-click for additional options
   - Use the delete button to remove trades

4. **Analyzing Performance**
   - Go to the "Statistics" tab
   - View key metrics and performance chart
   - Click "Update Statistics" to refresh

## Data Storage

The application stores data in two files:
- `trades.csv`: Contains all your trade records
- `trading_config.json`: Stores your account settings

These files are created automatically in the same directory as the application. 