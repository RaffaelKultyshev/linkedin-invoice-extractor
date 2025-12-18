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
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

# Config
ROOT = Path(__file__).parent
STATUS_FILE = ROOT / "status.json"
SIGNAL_FILE = ROOT / "continue_signal.txt"
PDF_DIR = ROOT / "pdfs"
SETTINGS_FILE = ROOT / "user_settings.json"

# Email config (TUG sender)
SMTP_SERVER = "smtp.mail.me.com"
SMTP_PORT = 587
SENDER_EMAIL = "raffael.kultyshev@icloud.com"
SENDER_PASSWORD = "anoq-rotn-bkrg-vqvk"

def load_status():
    if STATUS_FILE.exists():
        try:
            return json.loads(STATUS_FILE.read_text())
        except:
            pass
    return {"step": "", "waiting": False, "button_text": "", "pdf_path": ""}

def load_settings():
    if SETTINGS_FILE.exists():
        try:
            return json.loads(SETTINGS_FILE.read_text())
        except:
            pass
    return {"email": ""}

def save_settings(settings):
    SETTINGS_FILE.write_text(json.dumps(settings, indent=2))

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

def open_folder_in_finder(folder_path: Path):
    """Open folder in Finder (macOS)"""
    subprocess.run(["open", str(folder_path)])

def send_email_with_pdf(recipient_email: str, pdf_path: Path):
    """Send email with PDF attachment via iCloud SMTP"""
    now = datetime.now()
    date_str = now.strftime("%d/%m/%Y %H:%M")
    
    # Create message
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = recipient_email
    msg['Subject'] = "Your LinkedIn Invoice PDF"
    
    # Email body
    body = f"""Hi User,

Here is your PDF from your LinkedIn which you asked for on {date_str}.

Cheers,
TUG Team"""
    
    msg.attach(MIMEText(body, 'plain'))
    
    # Attach PDF
    try:
        with open(pdf_path, 'rb') as f:
            pdf_attachment = MIMEApplication(f.read(), _subtype='pdf')
            pdf_attachment.add_header('Content-Disposition', 'attachment', filename=pdf_path.name)
            msg.attach(pdf_attachment)
    except Exception as e:
        return f"Failed to attach PDF: {e}"
    
    # Send email
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        return f"SMTP Error: {e}"

def main():
    st.set_page_config(page_title="LinkedIn PDF Extractor", page_icon="📄", layout="wide")
    
    st.title("📄 LinkedIn Invoice PDF Extractor")
    st.caption("Extract your LinkedIn purchase history as PDF")
    
    st.divider()
    
    # Status display
    status = load_status()
    settings = load_settings()
    
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
    
    # Two big login buttons
    st.subheader("🚀 Extract PDF from LinkedIn")
    
    col_fast, col_validate = st.columns(2)
    
    with col_fast:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 10px; text-align: center; margin-bottom: 10px;">
            <h3 style="color: white; margin: 0;">⚡ FAST MODE</h3>
            <p style="color: rgba(255,255,255,0.8); margin: 5px 0 0 0; font-size: 14px;">Auto-proceeds after 10 sec</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("⚡ Login Fast", type="primary", use_container_width=True, key="fast_login"):
            clear_files()
            PDF_DIR.mkdir(exist_ok=True)
            
            # Start automation in FAST mode
            subprocess.Popen(
                [sys.executable, str(ROOT / "linkedin_automation.py"), "--fast"],
                cwd=str(ROOT)
            )
            st.success("🌐 Browser opening... Login quickly! (10 sec window)")
            time.sleep(2)
            st.rerun()
        
        st.caption("🏃 Login → script auto-continues after 10 seconds")
    
    with col_validate:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); padding: 20px; border-radius: 10px; text-align: center; margin-bottom: 10px;">
            <h3 style="color: white; margin: 0;">✅ VALIDATION MODE</h3>
            <p style="color: rgba(255,255,255,0.8); margin: 5px 0 0 0; font-size: 14px;">You control when to continue</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("✅ Login with Validation Check", use_container_width=True, key="validate_login"):
            clear_files()
            PDF_DIR.mkdir(exist_ok=True)
            
            # Start automation in normal mode
            subprocess.Popen(
                [sys.executable, str(ROOT / "linkedin_automation.py")],
                cwd=str(ROOT)
            )
            st.success("🌐 Browser opening... Log in and click the button when ready!")
            time.sleep(2)
            st.rerun()
        
        st.caption("🎯 Login → click \"I'M LOGGED IN\" when ready")
    
    st.divider()
    
    # Reset button
    col_reset, col_empty = st.columns([1, 3])
    with col_reset:
        if st.button("🔄 Reset / Clear Error", use_container_width=True):
            clear_files()
            st.success("Reset complete!")
            time.sleep(1)
            st.rerun()
    
    st.divider()
    
    # Display PDFs
    st.subheader("📁 Extracted PDFs")
    
    pdfs = get_pdfs()
    
    if pdfs:
        # Show latest PDF
        latest_pdf = pdfs[0]
        st.success(f"📄 Latest: **{latest_pdf.name}**")
        
        # Action buttons for the PDF
        col_dl, col_folder = st.columns(2)
        
        with col_dl:
            with open(latest_pdf, "rb") as f:
                st.download_button(
                    label="⬇️ Download PDF",
                    data=f.read(),
                    file_name=latest_pdf.name,
                    mime="application/pdf",
                    use_container_width=True
                )
        
        with col_folder:
            if st.button("📂 Open Folder", use_container_width=True, help="Open the folder where PDFs are saved"):
                open_folder_in_finder(PDF_DIR)
                st.toast("📂 Folder opened in Finder!")
        
        st.divider()
        
        # Email section
        st.subheader("📧 Send PDF to Email")
        
        email_col1, email_col2 = st.columns([2, 1])
        
        with email_col1:
            user_email = st.text_input(
                "Your email address",
                value=settings.get("email", ""),
                placeholder="your.email@example.com",
                help="Enter the email where you want to receive the PDF"
            )
            
            # Save email when it changes
            if user_email != settings.get("email", ""):
                settings["email"] = user_email
                save_settings(settings)
        
        with email_col2:
            st.write("")  # Spacer
            st.write("")  # Spacer
            if st.button("📨 Send PDF to Email", type="primary", use_container_width=True, disabled=not user_email):
                if user_email:
                    with st.spinner("Sending email..."):
                        result = send_email_with_pdf(user_email, latest_pdf)
                    
                    if result is True:
                        st.success("✅ Successfully sent the email with the PDF in it!")
                        st.balloons()
                    else:
                        st.error(f"❌ {result}")
                else:
                    st.warning("⚠️ Please enter your email address first")
        
        st.caption(f"📬 Email will be sent from **{SENDER_EMAIL}** (TUG Team)")
        
        st.divider()
        
        # Display PDF
        st.subheader("👀 PDF Preview")
        display_pdf(latest_pdf)
        
        # Show all PDFs
        if len(pdfs) > 1:
            with st.expander(f"📚 All PDFs ({len(pdfs)})"):
                for pdf in pdfs:
                    col1, col2, col3 = st.columns([3, 1, 1])
                    with col1:
                        st.text(pdf.name)
                    with col2:
                        with open(pdf, "rb") as f:
                            st.download_button(
                                label="⬇️",
                                data=f.read(),
                                file_name=pdf.name,
                                mime="application/pdf",
                                key=f"dl_{pdf.name}"
                            )
                    with col3:
                        if st.button("📨", key=f"email_{pdf.name}", help="Send this PDF to email"):
                            if settings.get("email"):
                                result = send_email_with_pdf(settings["email"], pdf)
                                if result is True:
                                    st.toast("✅ Email sent!")
                                else:
                                    st.toast(f"❌ {result}")
                            else:
                                st.toast("⚠️ Enter email first")
    else:
        st.info("No PDFs yet. Click one of the login buttons above to extract your LinkedIn purchases.")
    
    # Auto-refresh when waiting or processing
    if status.get("waiting") or (status.get("step") and "Done" not in status.get("step", "") and "Error" not in status.get("step", "")):
        time.sleep(2)
        st.rerun()

if __name__ == "__main__":
    main()
