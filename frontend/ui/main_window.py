"""
Main Window for SmartARTrainer
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout,
    QMessageBox, QStackedWidget
)
from PyQt6.QtCore import Qt

from frontend.utils.styles import get_main_stylesheet
from frontend.ui.login_screen import LoginScreen
from frontend.ui.fitness_form import FitnessForm
from frontend.ui.dashboard import Dashboard
from frontend.ui.workout_session import WorkoutSession
from frontend.ui.workout_demo import WorkoutDemo   # ✅ NEW
from frontend.ui.profile_screen import ProfileScreen
from frontend.ui.analytics_screen import AnalyticsScreen


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("SmartARTrainer")
        self.setMinimumSize(1000, 700)
        self.setStyleSheet(get_main_stylesheet())

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)

        self.stack = QStackedWidget()
        main_layout.addWidget(self.stack)

        # ================= Screens =================
        self.login_screen = LoginScreen(self)
        self.stack.addWidget(self.login_screen)

        self.fitness_form = FitnessForm(self)
        self.stack.addWidget(self.fitness_form)

        self.dashboard = Dashboard(self)
        self.stack.addWidget(self.dashboard)

        self.workout_demo = WorkoutDemo(self)          # ✅ NEW
        self.stack.addWidget(self.workout_demo)

        self.workout_session = WorkoutSession(self)
        self.stack.addWidget(self.workout_session)

        self.profile_screen = ProfileScreen(self)
        self.stack.addWidget(self.profile_screen)

        self.analytics_screen = AnalyticsScreen(self)
        self.stack.addWidget(self.analytics_screen)
        

        # ================= Data =================
        self.signup_data = {}
        self.fitness_data_cache = {}

        # ================= Signals =================
        self.login_screen.loginSuccess.connect(self.on_login_success)
        self.login_screen.registerContinue.connect(self.on_register_continue)

        self.fitness_form.backRequested.connect(self.on_fitness_back)
        self.fitness_form.formCompleted.connect(self.on_fitness_completed)
        self.dashboard.logoutSignal.connect(self.on_logout)

        self.workout_session.sessionEnded.connect(self.show_dashboard)
        self.workout_session.nextWorkoutRequested.connect(self.on_workout_finished)
        

        self.profile_screen.backRequested.connect(self.show_dashboard)
        self.analytics_screen.backRequested.connect(self.show_dashboard)
        

    # =====================================================
    def on_login_success(self, user_data):
        self.current_user = user_data
        self.dashboard.set_user(user_data)
        self.stack.setCurrentWidget(self.dashboard)

    def on_logout(self):
        self.current_user = None
        self.login_screen.clear_inputs()
        self.login_screen.show_login_tab()
        self.stack.setCurrentWidget(self.login_screen)
    
    def refresh_dashboard(self):
        """Helper to refresh dashboard after workout completion"""
        if hasattr(self, 'dashboard'):
            self.dashboard.refresh()

    # =====================================================
    def show_dashboard(self):
        self.stack.setCurrentWidget(self.dashboard)

    def show_workout_demo(self, workout_id):
        """Dashboard → Workout Demo"""
        self.workout_demo.load_workout(workout_id)
        self.stack.setCurrentWidget(self.workout_demo)

    def back_to_dashboard_from_demo(self):
        """Workout Demo → Dashboard"""
        self.stack.setCurrentWidget(self.dashboard)
        
    def show_workout_session(self, workout_id):
        """Workout Demo → Workout Session"""
        self.workout_session.set_workout(
            {"name": self.workout_demo.title_label.text()},
            workout_id
        )
        self.stack.setCurrentWidget(self.workout_session)
    

    def show_profile(self):
        if self.current_user:
            self.profile_screen.set_user(self.current_user)
            self.stack.setCurrentWidget(self.profile_screen)

    def show_analytics(self):
        if self.current_user:
            self.analytics_screen.set_user(self.current_user)
            self.stack.setCurrentWidget(self.analytics_screen)
    
    
    
    def on_workout_finished(self, workout_id):
        index = workout_id - 1   # ⭐ convert id → index

        if hasattr(self, 'dashboard'):
            self.dashboard.mark_exercise_completed(index)

        self.show_dashboard()

    # =====================================================
    def on_register_continue(self, signup_data):
        self.signup_data = signup_data
        self.fitness_form.set_data(self.fitness_data_cache)
        self.stack.setCurrentWidget(self.fitness_form)

    def on_fitness_back(self):
        self.fitness_data_cache = self.fitness_form.get_data()
        self.stack.setCurrentWidget(self.login_screen)

    def on_fitness_completed(self, fitness_data):
        from backend.models.data_manager import register_user

        success, message, _ = register_user(
            self.signup_data.get("name"),
            self.signup_data.get("email"),
            self.signup_data.get("password"),
            fitness_data
        )

        if success:
            QMessageBox.information(
                self,
                "Registration Successful",
                "Account created successfully.\nPlease login."
            )
            self.signup_data = {}
            self.fitness_data_cache = {}
            self.login_screen.clear_inputs()
            self.login_screen.show_login_tab()
            self.stack.setCurrentWidget(self.login_screen)
        else:
            QMessageBox.critical(self, "Registration Failed", message)
