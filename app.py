"""
LinkedIn Invoice PDF Extractor
Simple app to extract LinkedIn purchase history as PDF
"""

import streamlit as st
import json
import time
from pathlib import Path
import subprocess
import sys
import base64

# Config
ROOT = Path(__file__).parent
STATUS_FILE = ROOT / "status.json"
SIGNAL_FILE = ROOT / "continue_signal.txt"
PDF_DIR = ROOT / "pdfs"

def load_status():
    if STATUS_FILE.exists():
        try:
            return json.loads(STATUS_FILE.read_text())
        except:
            pass
    return {"step": "", "waiting": False, "button_text": "", "pdf_path": ""}

def send_continue_signal():
    SIGNAL_FILE.write_text("continue")

def clear_files():
    if STATUS_FILE.exists():
        STATUS_FILE.unlink()
    if SIGNAL_FILE.exists():
        SIGNAL_FILE.unlink()
    # Also delete all PDFs
    if PDF_DIR.exists():
        import shutil
        shutil.rmtree(PDF_DIR)
        PDF_DIR.mkdir(exist_ok=True)

def get_pdfs():
    """Get all PDFs in the pdfs folder"""
    PDF_DIR.mkdir(exist_ok=True)
    return sorted(PDF_DIR.glob("*.pdf"), key=lambda x: x.stat().st_mtime, reverse=True)

def display_pdf(pdf_path: Path):
    """Display PDF in Streamlit"""
    try:
        with open(pdf_path, "rb") as f:
            base64_pdf = base64.b64encode(f.read()).decode('utf-8')
        
        pdf_display = f'''
        <iframe 
            src="data:application/pdf;base64,{base64_pdf}" 
            width="100%" 
            height="600px" 
            type="application/pdf">
        </iframe>
        '''
        st.markdown(pdf_display, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Could not display PDF: {e}")

def main():
    st.set_page_config(page_title="LinkedIn PDF Extractor", page_icon="📄", layout="wide")
    
    st.title("📄 LinkedIn Invoice PDF Extractor")
    st.caption("Extract your LinkedIn purchase history as PDF")
    
    st.divider()
    
    # Status display
    status = load_status()
    
    # Only show login button when script is waiting for user
    if status.get("waiting"):
        st.markdown("---")
        st.warning(f"⏳ **{status.get('step')}**")
        st.markdown("### 👇 Click when you're done:")
        if st.button("✅ I'M LOGGED IN - CONTINUE!", type="primary", use_container_width=True, key="login_done"):
            send_continue_signal()
            st.success("✅ Signal sent! Script continuing...")
            time.sleep(1)
            st.rerun()
        st.markdown("---")
            
    elif status.get("step"):
        step_text = status.get("step", "")
        if "Error" in step_text:
            # Truncate long errors for display
            if len(step_text) > 150:
                step_text = step_text[:150] + "..."
            st.error(f"❌ {step_text}")
        elif "Done" in step_text or "Saved" in step_text:
            st.success(f"✅ {step_text}")
        else:
            st.info(f"⏳ {step_text}")
    
    st.divider()
    
    # Main action
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🚀 Extract PDF")
        
        if st.button("🔗 Start - Open LinkedIn Login", type="primary", use_container_width=True):
            clear_files()
            PDF_DIR.mkdir(exist_ok=True)
            
            # Start the automation script
            subprocess.Popen(
                [sys.executable, str(ROOT / "linkedin_automation.py")],
                cwd=str(ROOT)
            )
            st.success("🌐 Browser opening... Log in to LinkedIn!")
            time.sleep(2)
            st.rerun()
        
        if st.button("🔄 Reset / Clear Error", use_container_width=True):
            clear_files()
            st.success("Reset complete!")
            time.sleep(1)
            st.rerun()
    
    with col2:
        st.subheader("📋 Instructions")
        st.markdown("""
        1. Click **"Start - Open LinkedIn Login"**
        2. Browser opens (uses your real Chrome!)
        3. **Log in manually** - fingerprint/saved passwords work!
        4. Click **"I did the login ✅"** button above
        5. Script navigates to purchases page
        6. PDF is saved and displayed below
        """)
    
    st.divider()
    
    # Display PDFs
    st.subheader("📁 Extracted PDFs")
    
    pdfs = get_pdfs()
    
    if pdfs:
        # Show latest PDF
        latest_pdf = pdfs[0]
        st.success(f"📄 Latest: **{latest_pdf.name}**")
        
        # Download button
        with open(latest_pdf, "rb") as f:
            st.download_button(
                label="⬇️ Download PDF",
                data=f.read(),
                file_name=latest_pdf.name,
                mime="application/pdf",
                use_container_width=True
            )
        
        # Display PDF
        display_pdf(latest_pdf)
        
        # Show all PDFs
        if len(pdfs) > 1:
            with st.expander(f"📚 All PDFs ({len(pdfs)})"):
                for pdf in pdfs:
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.text(pdf.name)
                    with col2:
                        with open(pdf, "rb") as f:
                            st.download_button(
                                label="⬇️",
                                data=f.read(),
                                file_name=pdf.name,
                                mime="application/pdf",
                                key=pdf.name
                            )
    else:
        st.info("No PDFs yet. Click 'Start' to extract your LinkedIn purchases.")
    
    # Auto-refresh when waiting or processing
    if status.get("waiting") or (status.get("step") and "Done" not in status.get("step", "") and "Error" not in status.get("step", "")):
        time.sleep(2)
        st.rerun()

if __name__ == "__main__":
    main()
