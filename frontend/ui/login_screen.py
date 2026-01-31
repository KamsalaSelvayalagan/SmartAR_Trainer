"""
Login and Registration Screen for SmartARTrainer
Diagonal split design with static branding
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QFrame, QStackedWidget,
                             QCheckBox, QMessageBox, QGraphicsColorizeEffect)
from PyQt6.QtCore import Qt, pyqtSignal, QRect
from PyQt6.QtGui import QFont, QColor, QPalette, QPainter, QPainterPath, QLinearGradient


class DiagonalSplitWidget(QWidget):
    """Custom widget with diagonal split background"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(800, 600)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        width = self.width()
        height = self.height()
        
        # Draw white background for left side
        painter.fillRect(0, 0, width, height, QColor("#FFFFFF"))
        
        # Create diagonal gradient path
        path = QPainterPath()
        # Start from top-left of diagonal
        diagonal_start_x = int(width * 0.45)  # Diagonal starts at 45% of width
        
        # Create the diagonal polygon
        path.moveTo(diagonal_start_x, 0)  # Top of diagonal
        path.lineTo(width, 0)  # Top right
        path.lineTo(width, height)  # Bottom right
        path.lineTo(int(width * 0.35), height)  # Bottom of diagonal
        path.closeSubpath()
        
        # Create gradient
        gradient = QLinearGradient(diagonal_start_x, 0, width, height)
        gradient.setColorAt(0, QColor("#667eea"))
        gradient.setColorAt(1, QColor("#764ba2"))
        
        # Fill the diagonal section
        painter.fillPath(path, gradient)
        
        painter.end()


class LoginScreen(QWidget):
    """Login and Registration screen with diagonal split design"""
    
    loginSuccess = pyqtSignal(dict)    # Emits with user data dict
    registerContinue = pyqtSignal(dict) # Emits with registration data dict

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        """Initialize the UI"""
        # Set white background
        self.setStyleSheet("background: transparent;")
        
        # Create main layout with diagonal background
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Add diagonal split background
        self.diagonal_bg = DiagonalSplitWidget(self)
        self.diagonal_bg.setGeometry(0, 0, self.width(), self.height())
        self.diagonal_bg.lower()
        
        # Content layout
        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        # Left side - Branding (on white background)
        self.create_branding_section(content_layout)
        
        # Right side - Login/Register forms (on gradient)
        self.create_auth_section(content_layout)
        
        main_layout.addLayout(content_layout)
        
    def resizeEvent(self, event):
        """Handle resize to update diagonal background"""
        if hasattr(self, 'diagonal_bg'):
            self.diagonal_bg.setGeometry(0, 0, self.width(), self.height())
        super().resizeEvent(event)
        
    def create_branding_section(self, parent_layout):
        """Create the left branding section"""
        branding_frame = QFrame()
        branding_frame.setStyleSheet("background: transparent;")
        
        branding_layout = QVBoxLayout(branding_frame)
        branding_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        branding_layout.setContentsMargins(40, 40, 40, 40)
        
        branding_layout.setSpacing(0)
        
        # Logo
        logo_label = QLabel()
        try:
            from PyQt6.QtGui import QPixmap
            logo_pixmap = QPixmap("frontend/assets/logo.png")
            if not logo_pixmap.isNull():
                # Scale logo
                scaled_logo = logo_pixmap.scaled(250, 250, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                logo_label.setPixmap(scaled_logo)
                logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                
                # Apply color overlay using QGraphicsColorizeEffect (Safe Method)
                color_effect = QGraphicsColorizeEffect()
                color_effect.setColor(QColor("#667eea"))
                color_effect.setStrength(1.0) # Ensure maximum color strength
                logo_label.setGraphicsEffect(color_effect)
                
                branding_layout.addWidget(logo_label)
        except Exception as e:
            print(f"Error loading logo: {e}")

        # Tagline
        tagline = QLabel("Your AI-Powered Fitness Coach")
        tagline.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        tagline.setStyleSheet("color: #667eea; margin-top: 0px; background: transparent;")
        tagline.setAlignment(Qt.AlignmentFlag.AlignCenter)
        branding_layout.addWidget(tagline)
        
        parent_layout.addWidget(branding_frame, 45)  # 45% width
        
    def create_auth_section(self, parent_layout):
        """Create the right authentication section"""
        auth_frame = QFrame()
        auth_frame.setStyleSheet("background: transparent;")
        
        auth_layout = QVBoxLayout(auth_frame)
        auth_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        auth_layout.setContentsMargins(60, 40, 60, 40)
        
        # Stacked widget for login/register forms
        self.form_stack = QStackedWidget()
        self.form_stack.setStyleSheet("background: transparent;")
        
        # Login form
        login_widget = self.create_login_form()
        self.form_stack.addWidget(login_widget)
        
        # Register form
        register_widget = self.create_register_form()
        self.form_stack.addWidget(register_widget)
        
        auth_layout.addWidget(self.form_stack)
        
        parent_layout.addWidget(auth_frame, 55)  # 55% width
        
    def create_login_form(self):
        """Create login form"""
        widget = QWidget()
        widget.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Title
        title = QLabel("Welcome Back")
        title.setFont(QFont("Segoe UI", 32, QFont.Weight.Bold))
        title.setStyleSheet("color: white; background: transparent;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Subtitle
        subtitle = QLabel("Login to your account")
        subtitle.setFont(QFont("Segoe UI", 14))
        subtitle.setStyleSheet("color: rgba(255, 255, 255, 0.9); margin-bottom: 20px; background: transparent;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)
        
        # Email field
        self.login_email = QLineEdit()
        self.login_email.setPlaceholderText("Registered email")
        self.login_email.setMinimumHeight(45)
        self.login_email.setStyleSheet(self.get_input_style())
        layout.addWidget(self.login_email)
        
        # Password field
        self.login_password = QLineEdit()
        self.login_password.setPlaceholderText("Enter your password")
        self.login_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.login_password.setMinimumHeight(45)
        self.login_password.setStyleSheet(self.get_input_style())
        layout.addWidget(self.login_password)
        
        # Remember me checkbox
        remember_layout = QHBoxLayout()
        remember_cb = QCheckBox("Remember me")
        remember_cb.setStyleSheet("color: white; background: transparent;")
        remember_layout.addWidget(remember_cb)
        remember_layout.addStretch()
        layout.addLayout(remember_layout)
        
        # Login button
        login_btn = QPushButton("SIGN IN")
        login_btn.setMinimumHeight(45)
        login_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        login_btn.setStyleSheet(self.get_button_style())
        login_btn.clicked.connect(self.handle_login)
        layout.addWidget(login_btn)

        # Switch to register
        switch_layout = QHBoxLayout()
        switch_label = QLabel("Don't have an account?")
        switch_label.setStyleSheet("color: rgba(255, 255, 255, 0.9); background: transparent;")
        
        switch_btn = QPushButton("Sign Up")
        switch_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: white;
                border: none;
                text-decoration: underline;
                font-weight: bold;
            }
            QPushButton:hover {
                color: #e0e0e0;
            }
        """)
        switch_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        switch_btn.clicked.connect(lambda: self.form_stack.setCurrentIndex(1))
        
        switch_layout.addStretch()
        switch_layout.addWidget(switch_label)
        switch_layout.addWidget(switch_btn)
        switch_layout.addStretch()
        
        layout.addLayout(switch_layout)
        
        return widget
        
    def create_register_form(self):
        """Create registration form"""
        widget = QWidget()
        widget.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(40, 20, 40, 20)
        
        # Title
        title = QLabel("Create Account")
        title.setFont(QFont("Segoe UI", 32, QFont.Weight.Bold))
        title.setStyleSheet("color: white; background: transparent;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Subtitle
        subtitle = QLabel("Start your fitness journey")
        subtitle.setFont(QFont("Segoe UI", 14))
        subtitle.setStyleSheet("color: rgba(255, 255, 255, 0.9); margin-bottom: 15px; background: transparent;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)
        
        self.register_username = QLineEdit()
        self.register_username.setPlaceholderText("Name")
        self.register_username.setMinimumHeight(45)
        self.register_username.setStyleSheet(self.get_input_style())
        self.register_username.textChanged.connect(self.check_register_fields)
        layout.addWidget(self.register_username)
        
        # Email field
        self.register_email = QLineEdit()
        self.register_email.setPlaceholderText("Email")
        self.register_email.setMinimumHeight(45)
        self.register_email.setStyleSheet(self.get_input_style())
        self.register_email.textChanged.connect(self.check_register_fields)
        layout.addWidget(self.register_email)
        
        # Password field
        self.register_password = QLineEdit()
        self.register_password.setPlaceholderText("Password")
        self.register_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.register_password.setMinimumHeight(45)
        self.register_password.setStyleSheet(self.get_input_style())
        self.register_password.textChanged.connect(self.check_register_fields)
        layout.addWidget(self.register_password)
        
        # Confirm password field
        self.register_confirm = QLineEdit()
        self.register_confirm.setPlaceholderText("Confirm Password")
        self.register_confirm.setEchoMode(QLineEdit.EchoMode.Password)
        self.register_confirm.setMinimumHeight(45)
        self.register_confirm.setStyleSheet(self.get_input_style())
        self.register_confirm.textChanged.connect(self.check_register_fields)
        layout.addWidget(self.register_confirm)
        
        # Register button
        self.register_btn = QPushButton("SIGN UP")
        self.register_btn.setMinimumHeight(45)
        self.register_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.register_btn.setStyleSheet(self.get_button_style())
        self.register_btn.clicked.connect(self.handle_register)
        layout.addWidget(self.register_btn)
        
        # Switch to login
        switch_layout = QHBoxLayout()
        switch_label = QLabel("Already have an account?")
        switch_label.setStyleSheet("color: rgba(255, 255, 255, 0.9); background: transparent;")
        
        switch_btn = QPushButton("Log In")
        switch_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: white;
                border: none;
                text-decoration: underline;
                font-weight: bold;
            }
            QPushButton:hover {
                color: #e0e0e0;
            }
        """)
        switch_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        switch_btn.clicked.connect(lambda: self.form_stack.setCurrentIndex(0))
        
        switch_layout.addStretch()
        switch_layout.addWidget(switch_label)
        switch_layout.addWidget(switch_btn)
        switch_layout.addStretch()
        
        layout.addLayout(switch_layout)
        
        return widget

    def get_input_style(self):
        """Return stylesheet for input fields"""
        return """
            QLineEdit {
                background-color: white;
                border: none;
                border-radius: 22px;
                padding: 0 20px;
                font-size: 14px;
                color: #333333;
            }
            QLineEdit:focus {
                background-color: #f5f5f5;
            }
        """

    def get_button_style(self):
        """Return stylesheet for primary buttons"""
        return """
            QPushButton {
                background: rgba(255, 255, 255, 0.3);
                color: white;
                border: 2px solid white;
                border-radius: 22px;
                font-weight: bold;
                font-size: 14px;
                letter-spacing: 1px;
            }
            QPushButton:hover {
                background: white;
                color: #667eea;
            }
        """

    def handle_login(self):
        """Handle login button click"""
        email = self.login_email.text().strip()
        password = self.login_password.text()
        
        if not email or not password:
            QMessageBox.warning(self, "Error", "Please fill in all fields")
            return

        from backend.models.data_manager import login_user
        
        success, message, user_data = login_user(email, password)
        
        if success:
            self.loginSuccess.emit(user_data)
        else:
            QMessageBox.critical(self, "Login Failed", message)
            
    def check_register_fields(self):
        """Update button text based on field population"""
        username = self.register_username.text().strip()
        email = self.register_email.text().strip()
        password = self.register_password.text()
        confirm = self.register_confirm.text()
        
        if all([username, email, password, confirm]):
            self.register_btn.setText("CONTINUE")
        else:
            self.register_btn.setText("SIGN UP")

    def handle_register(self):
        """Handle registration button click (Continue to fitness form)"""
        username = self.register_username.text().strip()
        email = self.register_email.text().strip()
        password = self.register_password.text()
        confirm = self.register_confirm.text()
        
        if not all([username, email, password, confirm]):
            QMessageBox.warning(self, "Error", "Please fill in all fields")
            return
            
        if password != confirm:
            QMessageBox.warning(self, "Error", "Passwords do not match")
            return

        # Instead of registering now, emit signal to continue to fitness form
        reg_data = {
            "name": username,
            "email": email,
            "password": password
        }
        self.registerContinue.emit(reg_data)

    def clear_inputs(self):
        """Clear login and registration inputs"""
        self.login_email.clear()
        self.login_password.clear()
        self.register_username.clear()
        self.register_email.clear()
        self.register_password.clear()
        self.register_confirm.clear()

    def show_login_tab(self):
        """Switch to login tab"""
        self.form_stack.setCurrentIndex(0)

    def show_register_tab(self):
        """Switch to register tab"""
        self.form_stack.setCurrentIndex(1)

