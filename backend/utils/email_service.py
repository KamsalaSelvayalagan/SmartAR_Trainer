import os
import random
import string
import smtplib
import ssl
from email.message import EmailMessage
from PyQt6.QtWidgets import (
    QMessageBox, QDialog, QVBoxLayout, QLabel, 
    QLineEdit, QPushButton, QHBoxLayout
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

def generate_otp(length=6):
    """Generate a random numeric OTP"""
    return ''.join(random.choices(string.digits, k=length))


def send_otp_email(recipient_email: str, otp: str) -> tuple[bool, str]:
    """Send OTP via SMTP using environment-configured credentials.

    Expects the following environment variables (recommended):
      - SMTP_HOST
      - SMTP_PORT
      - SMTP_USER
      - SMTP_PASS
      - SMTP_FROM (optional; defaults to SMTP_USER)
      - SMTP_USE_SSL (optional; 'true' enables SSL)
      - SMTP_STARTTLS (optional; 'true' enables STARTTLS)

    Returns (success: bool, message: str).
    """
    host = os.getenv("SMTP_HOST")
    port = os.getenv("SMTP_PORT")
    user = os.getenv("SMTP_USER")
    password = os.getenv("SMTP_PASS")
    use_ssl = os.getenv("SMTP_USE_SSL", "false").lower() == "true"
    starttls = os.getenv("SMTP_STARTTLS", "true").lower() == "true"
    from_addr = os.getenv("SMTP_FROM", user)

    if not (host and port and user and password):
        return False, "SMTP credentials not configured"

    try:
        port_int = int(port)
    except Exception:
        return False, "Invalid SMTP_PORT"

    msg = EmailMessage()
    msg["Subject"] = "Your verification code"
    msg["From"] = from_addr
    msg["To"] = recipient_email
    msg.set_content(f"Your verification code is: {otp}\nThis code will expire in 10 minutes.")

    try:
        if use_ssl:
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(host, port_int, context=context) as server:
                server.login(user, password)
                server.send_message(msg)
        else:
            with smtplib.SMTP(host, port_int, timeout=10) as server:
                server.ehlo()
                if starttls:
                    server.starttls(context=ssl.create_default_context())
                    server.ehlo()
                server.login(user, password)
                server.send_message(msg)
        return True, "Email sent"
    except Exception as e:
        return False, str(e)


def send_otp(email, otp, parent=None, purpose="Verification"):
    """Attempt to send OTP via SMTP, fallback to simulated dialog on failure.

    Returns True if real send succeeded, False if fallback was used.
    """
    ok, msg = send_otp_email(email, otp)
    if ok:
        try:
            # Inform user a verification email was sent
            if parent:
                QMessageBox.information(parent, "Verification Sent", f"A verification code was sent to {email}.")
        except Exception:
            pass
        return True

    # Fallback: show simulated in-app dialog and inform of failure
    try:
        if parent:
            QMessageBox.warning(parent, "Email Send Failed", f"Failed to send verification email: {msg}\nShowing in-app code instead.")
    except Exception:
        pass
    send_otp_simulated(email, otp, parent, purpose)
    return False

def send_otp_simulated(email, otp, parent=None, purpose="Password Reset Request"):
    """
    Compact simulated OTP notification to remove empty space.
    """
    dialog = QDialog(parent)
    dialog.setWindowTitle(purpose)
    dialog.setMinimumWidth(320)
    
    layout = QVBoxLayout(dialog)
    layout.setContentsMargins(20, 20, 20, 20)
    layout.setSpacing(10)
    
    dialog.setStyleSheet("""
        QDialog {
            background-color: #0f172a;
            border: 1px solid #334155;
            border-radius: 10px;
        }
        QLabel {
            color: #f1f5f9;
            font-size: 13px;
            font-family: 'Segoe UI', sans-serif;
        }
        QPushButton {
            background-color: #334155;
            color: white;
            border-radius: 5px;
            padding: 6px 20px;
            font-weight: bold;
            border: 1px solid #475569;
        }
        QPushButton:hover {
            background-color: #475569;
        }
    """)
    
    content = QLabel(
        f"<b>To:</b> {email}<br>"
        f"<b>Your Verification Code:</b> <b style='color:#667eea;'>{otp}</b><br><br>"
        f"Please enter this code in the application to proceed.<br>"
        f"This code will expire in 10 minutes."
    )
    content.setWordWrap(True)
    layout.addWidget(content)
    
    btn_layout = QHBoxLayout()
    btn_layout.addStretch()
    ok_btn = QPushButton("OK")
    ok_btn.setCursor(Qt.CursorShape(13))
    ok_btn.clicked.connect(dialog.accept)
    btn_layout.addWidget(ok_btn)
    layout.addLayout(btn_layout)
    
    dialog.exec()


class OTPInputDialog(QDialog):
    """Custom styled dialog for entering OTP"""
    def __init__(self, email, title="Verify OTP", description=None, parent=None):
        super().__init__(parent)
        self.email = email
        self.dialog_title = title
        self.dialog_description = description or f"Enter the 6-digit code sent to\n{self.email}"
        self.otp_value = ""
        self.resend_callback = None # Can be set to a function that regenerates and resends
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(self.dialog_title)
        self.setFixedWidth(460) # Increased width to accommodate long emails
        self.setMinimumHeight(320)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        
        self.setStyleSheet("""
            QDialog {
                background-color: #0f172a;
                border: 2px solid #334155;
                border-radius: 20px;
            }
            QLabel {
                color: #f1f5f9;
                background: transparent;
            }
            QLineEdit {
                background-color: #1e293b;
                border: 1px solid #334155;
                border-radius: 8px;
                padding: 10px;
                color: white;
                font-size: 18px;
                letter-spacing: 5px;
                font-weight: bold;
            }
            QPushButton#verify_btn {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                   stop:0 #667eea, stop:1 #764ba2);
                color: white;
                border-radius: 8px;
                font-weight: bold;
                padding: 10px;
                font-size: 14px;
            }
            QPushButton#verify_btn:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                   stop:0 #764ba2, stop:1 #667eea);
            }
            QPushButton#cancel_btn {
                background: transparent;
                color: #94a3b8;
                border: 1px solid #334155;
                border-radius: 8px;
                padding: 10px;
            }
            QPushButton#cancel_btn:hover {
                color: white;
                border-color: #475569;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        title = QLabel(self.dialog_title)
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        desc = QLabel(self.dialog_description)
        desc.setFont(QFont("Segoe UI", 10))
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #94a3b8; padding: 0 10px;")
        layout.addWidget(desc)

        self.otp_input = QLineEdit()
        self.otp_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.otp_input.setMaxLength(6)
        self.otp_input.setPlaceholderText("· · · · · ·")
        self.otp_input.setMinimumHeight(50)
        layout.addWidget(self.otp_input)

        # Resend Option
        resend_layout = QHBoxLayout()
        resend_layout.setContentsMargins(0, 0, 0, 0)
        resend_text = QLabel("Didn't receive the code?")
        resend_text.setStyleSheet("color: #64748b; font-size: 11px;")
        
        self.resend_btn = QPushButton("Resend OTP")
        self.resend_btn.setCursor(Qt.CursorShape(13))
        self.resend_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #667eea;
                border: none;
                font-size: 11px;
                font-weight: bold;
                text-decoration: underline;
            }
            QPushButton:hover {
                color: #764ba2;
            }
        """)
        self.resend_btn.clicked.connect(self.on_resend)
        
        resend_layout.addStretch()
        resend_layout.addWidget(resend_text)
        resend_layout.addWidget(self.resend_btn)
        resend_layout.addStretch()
        layout.addLayout(resend_layout)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("cancel_btn")
        cancel_btn.setCursor(Qt.CursorShape(13))
        cancel_btn.setMinimumHeight(45)
        cancel_btn.clicked.connect(self.reject)
        
        verify_btn = QPushButton("Verify Account")
        verify_btn.setObjectName("verify_btn")
        verify_btn.setCursor(Qt.CursorShape(13))
        verify_btn.setMinimumHeight(45)
        verify_btn.clicked.connect(self.on_verify)

        btn_layout.addWidget(cancel_btn, 1)
        btn_layout.addWidget(verify_btn, 2)
        layout.addLayout(btn_layout)

    def on_resend(self):
        """Simulate resending the OTP"""
        if self.resend_callback:
            self.resend_callback()
            QMessageBox.information(self, "OTP Resent", "A new verification code has been sent to your email.")
        else:
            # Default behavior if no callback
            QMessageBox.information(self, "OTP Resent", "Verification code has been resent to your email.")

    def on_verify(self):
        self.otp_value = self.otp_input.text().strip()
        if len(self.otp_value) == 6:
            self.accept()
        else:
            QMessageBox.warning(self, "Invalid OTP", "Please enter a 6-digit code.")

    @staticmethod
    def get_otp(email, title="Verify OTP", description=None, parent=None, resend_callback=None):
        dialog = OTPInputDialog(email, title, description, parent)
        dialog.resend_callback = resend_callback
        if dialog.exec() == QDialog.DialogCode.Accepted:
            return dialog.otp_value, True
        return "", False
