# LinkedIn Invoice PDF Extractor

Extract your LinkedIn purchase history as PDF with one click.

## Requirements
- Mac with Chrome installed
- Python 3.8+

## Quick Start

### 1. Install (one time)

```bash
git clone https://github.com/RaffaelKultyshev/linkedin-invoice-extractor.git
cd linkedin-invoice-extractor
pip install streamlit
```

### 2. Close ALL Chrome windows (important!)

### 3. Run the app

```bash
streamlit run app.py --server.port 3940
```

### 4. Open in browser

Go to: http://localhost:3940

### 5. Use the app

1. Click **"🚀 Start - Open LinkedIn Login"**
2. LinkedIn opens in Chrome → Log in with your credentials (fingerprint works!)
3. Click **"✅ I'M LOGGED IN - CONTINUE!"** in the app
4. Wait 5 seconds → Script automatically:
   - Goes to purchases page
   - Opens print dialog
   - Saves as PDF
5. PDF appears in the app! 🎉

## Notes

- Uses YOUR Chrome browser (not a bot), so saved passwords work
- Your saved passwords & fingerprint work
- PDF is saved locally in the `pdfs/` folder
- **Zero credentials stored** - we never see your password

## Troubleshooting

- If it asks for permission → Allow "System Events" access
- If print dialog doesn't open → Click Reset and try again

## Security

✅ Zero credential storage - you log in yourself via your own browser  
✅ All data stays local on your machine  
✅ No network calls to external servers
