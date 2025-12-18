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

## Two Login Modes

### ⚡ Fast Mode (Recommended)
1. Click **"⚡ Login Fast"**
2. Log in quickly (10 second window)
3. Script auto-continues → PDF ready!
4. **No extra clicks needed!**

### ✅ Validation Mode
1. Click **"✅ Login with Validation Check"**
2. Log in to LinkedIn (take your time)
3. Click **"I'M LOGGED IN - CONTINUE!"**
4. Script continues → PDF ready!

## Features

- 📄 **One-click PDF extraction** - Saves LinkedIn purchases as PDF
- ⚡ **Fast Mode** - Just login, everything else is automatic
- 📧 **Email sending** - Send PDF to any email address instantly
- 📂 **Open folder** - Quick access to saved PDFs
- 👀 **PDF preview** - View PDFs directly in the app

## Notes

- Uses YOUR Chrome browser (not a bot), so saved passwords work
- Your saved passwords & fingerprint work
- PDF is saved locally in the `pdfs/` folder
- **Zero credentials stored** - we never see your password

## Troubleshooting

- If it asks for permission → Allow "System Events" access
- If print dialog doesn't open → Click Reset and try again
- If 10 seconds is too short → Use "Validation Mode" instead

## Security

✅ Zero credential storage - you log in yourself via your own browser  
✅ All data stays local on your machine  
✅ No network calls to external servers (except email sending via TUG Team)
