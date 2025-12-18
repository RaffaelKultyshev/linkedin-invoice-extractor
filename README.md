# LinkedIn Invoice PDF Extractor

Extract your LinkedIn purchase history as PDF with one click.

## Requirements
- Mac with Chrome installed
- Python 3.11+ with conda

## Quick Start

### 1. Install (one time)
```bash
cd LinkedinLogin
pip install streamlit
```

### 2. Run the app
```bash
cd LinkedinLogin
streamlit run app.py --server.port 3940
```

### 3. Open in browser
Go to: http://localhost:3940

### 4. Use the app
1. Click **"Start - Open LinkedIn Login"**
2. Log in to LinkedIn (use your fingerprint/saved password)
3. Click **"I'M LOGGED IN - CONTINUE!"**
4. Script automatically:
   - Goes to purchases page
   - Opens print dialog
   - Saves as PDF
5. PDF appears in the app!

## Notes
- Uses YOUR Chrome browser (not a bot)
- Your saved passwords & fingerprint work
- PDF is saved locally

## Troubleshooting
- If it asks for permission → Allow "System Events" access
- If print dialog doesn't open → Click Reset and try again

