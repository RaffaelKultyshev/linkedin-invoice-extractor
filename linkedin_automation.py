"""
LinkedIn Invoice PDF Extractor
YOU only login - script does EVERYTHING else using AppleScript to control Chrome!
"""

import json
import time
import subprocess
import shutil
import sys
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).parent
STATUS_FILE = ROOT / "status.json"
SIGNAL_FILE = ROOT / "continue_signal.txt"
PDF_DIR = ROOT / "pdfs"

def update_status(step, waiting=False, button_text="", pdf_path=""):
    print(f"[STATUS] {step}")
    STATUS_FILE.write_text(json.dumps({
        "step": step,
        "waiting": waiting,
        "button_text": button_text,
        "pdf_path": pdf_path
    }))

def wait_for_user_signal(timeout=300):
    start = time.time()
    while time.time() - start < timeout:
        if SIGNAL_FILE.exists():
            SIGNAL_FILE.unlink()
            return True
        time.sleep(1)
    return False

def run_applescript(script):
    """Run AppleScript to control Chrome"""
    result = subprocess.run(
        ["osascript", "-e", script],
        capture_output=True,
        text=True
    )
    return result.stdout.strip()

def run_automation(fast_mode=False):
    PDF_DIR.mkdir(exist_ok=True)
    
    if STATUS_FILE.exists():
        STATUS_FILE.unlink()
    if SIGNAL_FILE.exists():
        SIGNAL_FILE.unlink()
    
    # STEP 1: Open LinkedIn login in Chrome
    update_status("Opening LinkedIn in Chrome...")
    
    run_applescript('''
        tell application "Google Chrome"
            activate
            open location "https://www.linkedin.com/login"
        end tell
    ''')
    
    if fast_mode:
        # Fast mode: assume user is already logged in or will be quickly
        update_status("⚡ Fast Mode: Waiting 10 seconds for login...")
        time.sleep(10)  # Give user 10 seconds to login
    else:
        # Normal mode: wait for user confirmation
        time.sleep(3)
        
        # STEP 2: Wait for user to login (ONLY thing user does!)
        update_status(
            "Log in with fingerprint/saved password. Click button when you're logged in.",
            waiting=True,
            button_text="I'm logged in ✅"
        )
        
        if not wait_for_user_signal(timeout=300):
            update_status("Error: Timeout waiting for login")
            return
        
        time.sleep(2)
    
    # STEP 3: Navigate to purchases page (AUTOMATIC!)
    update_status("Navigating to purchases page...")
    
    # Find LinkedIn tab, switch to it, use Command+L to select URL bar, type new URL
    run_applescript('''
        tell application "Google Chrome"
            -- Find the LinkedIn tab
            repeat with w in windows
                set tabIndex to 1
                repeat with t in tabs of w
                    if URL of t contains "linkedin.com" then
                        -- Switch to this window and tab
                        set index of w to 1
                        set active tab index of w to tabIndex
                        activate
                        delay 1
                        
                        -- Use Command+L to select URL bar (not Ctrl+F!)
                        tell application "System Events"
                            keystroke "l" using command down
                            delay 0.5
                            -- Type the new URL
                            keystroke "https://www.linkedin.com/manage/purchases-payments/purchases/"
                            delay 0.3
                            -- Press Enter to navigate
                            keystroke return
                        end tell
                        return
                    end if
                    set tabIndex to tabIndex + 1
                end repeat
            end repeat
        end tell
    ''')
    
    time.sleep(5)
    
    # STEP 4: Save as PDF using AppleScript (AUTOMATIC!)
    update_status("Saving page as PDF...")
    
    # Create unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    pdf_name = f"LinkedIn_Purchases_{timestamp}.pdf"
    pdf_path = PDF_DIR / pdf_name
    
    # Click on page first to dismiss any search bar, then Command+P
    run_applescript('''
        tell application "Google Chrome"
            repeat with w in windows
                set tabIndex to 1
                repeat with t in tabs of w
                    if URL of t contains "linkedin.com" then
                        -- Switch to LinkedIn tab
                        set index of w to 1
                        set active tab index of w to tabIndex
                        activate
                        delay 1
                        
                        tell application "System Events"
                            -- Press Escape to close any search bar/popup
                            key code 53
                            delay 0.5
                            
                            -- Click in the middle of the page to focus it
                            tell process "Google Chrome"
                                click at {640, 400}
                            end tell
                            delay 0.5
                            
                            -- Press Escape again just to be safe
                            key code 53
                            delay 0.5
                            
                            -- Now Command+P to print
                            keystroke "p" using command down
                        end tell
                        return
                    end if
                    set tabIndex to tabIndex + 1
                end repeat
            end repeat
        end tell
    ''')
    
    time.sleep(2)
    
    # Click on the PDF dropdown and select "Save as PDF"
    # Then save to our folder
    run_applescript(f'''
        tell application "System Events"
            tell process "Google Chrome"
                -- Wait for print dialog
                delay 1
                
                -- Click the destination dropdown (usually shows "Save as PDF")
                -- Try to find and click Save as PDF option
                try
                    click pop up button 1 of sheet 1 of window 1
                    delay 0.5
                    click menu item "Save as PDF" of menu 1 of pop up button 1 of sheet 1 of window 1
                    delay 0.5
                end try
                
                -- Click Save button
                delay 1
                keystroke return
                delay 1
                
                -- Type the filename
                keystroke "g" using {{command down, shift down}}
                delay 0.5
                keystroke "{pdf_path}"
                delay 0.5
                keystroke return
                delay 0.5
                keystroke return
            end tell
        end tell
    ''')
    
    time.sleep(3)
    
    # Alternative: Check Desktop for recent PDF
    update_status("Looking for saved PDF...")
    
    desktop = Path.home() / "Desktop"
    downloads = Path.home() / "Downloads"
    
    # Wait a bit for file to be saved
    time.sleep(2)
    
    # Look for recent PDFs
    found_pdf = None
    for folder in [desktop, downloads, PDF_DIR]:
        if folder.exists():
            pdfs = list(folder.glob("*.pdf"))
            if pdfs:
                recent = max(pdfs, key=lambda p: p.stat().st_mtime)
                # Check if it's recent (last 60 seconds)
                if time.time() - recent.stat().st_mtime < 60:
                    found_pdf = recent
                    break
    
    if found_pdf and found_pdf.parent != PDF_DIR:
        # Copy to our folder
        dest = PDF_DIR / pdf_name
        shutil.copy(found_pdf, dest)
        update_status(f"Done! Saved: {pdf_name}", pdf_path=str(dest))
    elif (PDF_DIR / pdf_name).exists():
        update_status(f"Done! Saved: {pdf_name}", pdf_path=str(PDF_DIR / pdf_name))
    else:
        # Manual fallback
        update_status(
            "Almost done! Save the PDF manually (Cmd+P → Save as PDF → Desktop). Click when done.",
            waiting=True,
            button_text="I saved the PDF ✅"
        )
        
        if wait_for_user_signal(timeout=120):
            # Find the PDF
            for folder in [desktop, downloads]:
                pdfs = list(folder.glob("*.pdf"))
                if pdfs:
                    recent = max(pdfs, key=lambda p: p.stat().st_mtime)
                    if time.time() - recent.stat().st_mtime < 120:
                        dest = PDF_DIR / pdf_name
                        shutil.copy(recent, dest)
                        update_status(f"Done! Saved: {pdf_name}", pdf_path=str(dest))
                        return
            
            update_status("Done! Check your Desktop for the PDF.")
        else:
            update_status("Timeout. Check Desktop for the PDF.")

if __name__ == "__main__":
    # Check for --fast flag
    fast_mode = "--fast" in sys.argv
    run_automation(fast_mode=fast_mode)
