"""
data_manager.py
Handles ALL SQLite database operations for SmartARTrainer
"""

import sqlite3
from backend.models.db_config import get_db_connection, close_connection

# =====================================================
# REGISTRATION & LOGIN
# =====================================================

def determine_plan_id(fitness_data):
    if not fitness_data or not fitness_data.get('workout_experience'):
        return 1

    experience = fitness_data.get('workout_experience', '').lower()

    if 'beginner' in experience or 'none' in experience:
        return 1
    elif 'intermediate' in experience or 'moderate' in experience:
        return 2
    elif 'advanced' in experience or 'expert' in experience:
        return 3
    return 1


def register_user(name, email, password, fitness_data=None):
    connection = get_db_connection()
    if not connection:
        return False, "Database connection failed", None

    try:
        cursor = connection.cursor()

        if fitness_data:
            plan_id = determine_plan_id(fitness_data)

            query = """
                INSERT INTO trainee (
                    name, email, pwd, dob, gender, height, weight,
                    workout_experience, workout_duration, weekly_frequency, plan_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            params = (
                name, email, password,
                fitness_data.get('dob'),
                fitness_data.get('gender'),
                fitness_data.get('height'),
                fitness_data.get('weight'),
                fitness_data.get('workout_experience'),
                fitness_data.get('workout_duration'),
                fitness_data.get('weekly_frequency'),
                plan_id
            )
        else:
            query = "INSERT INTO trainee (name, email, pwd, plan_id) VALUES (?, ?, ?, ?)"
            params = (name, email, password, 1)

        cursor.execute(query, params)
        connection.commit()
        return True, "Registration successful", cursor.lastrowid

    except sqlite3.IntegrityError:
        return False, "Email already exists", None
    except sqlite3.Error as e:
        return False, f"Database error: {e}", None
    finally:
        close_connection(connection, cursor)


def login_user(email, password):
    connection = get_db_connection()
    if not connection:
        return False, "Database connection failed", None

    try:
        cursor = connection.cursor()
        cursor.execute(
            "SELECT trainee_id, name, email FROM trainee WHERE email = ? AND pwd = ?",
            (email, password)
        )
        row = cursor.fetchone()
        return (True, "Login successful", dict(row)) if row else (False, "Invalid email or password", None)
    finally:
        close_connection(connection, cursor)

# =====================================================
# WORKOUT DEMO (USED BY WorkoutDemo UI)
# =====================================================

def get_workout_by_id(workout_id):
    connection = get_db_connection()
    if not connection:
        return None

    try:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT workout_name, video_url, description
            FROM workout
            WHERE workout_id = ?
        """, (workout_id,))
        return cursor.fetchone()
    finally:
        close_connection(connection, cursor)


def get_all_workouts():
    connection = get_db_connection()
    if not connection:
        return []

    try:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT workout_id, workout_name, video_url, description
            FROM workout
            ORDER BY workout_id
        """)
        return cursor.fetchall()
    finally:
        close_connection(connection, cursor)

# =====================================================
# DASHBOARD & WORKOUT PLAN
# =====================================================

WORKOUT_COLUMNS = [
    "jumpingjack_crt",
    "pushup_crt",
    "plank_time",
    "crunches_crt",
    "squat_crt",
    "cobrastretch_time"
]


def get_trainee_info(trainee_id):
    connection = get_db_connection()
    if not connection:
        return None

    try:
        cursor = connection.cursor()
        # Add 'fitness_level' to the query here
        cursor.execute("""
            SELECT trainee_id, name, plan_id, fitness_level
            FROM trainee WHERE trainee_id = ?
        """, (trainee_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        close_connection(connection, cursor)


"""
def get_workout_plan(plan_id):
    connection = get_db_connection()
    if not connection:
        return []

    try:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM workout_plan WHERE plan_id = ?", (plan_id,))
        row = cursor.fetchone()
        if not row:
            return []

        return [
            {"name": "Jumping Jacks", "target": row["jumpingjack_count"]},
            {"name": "Push Ups", "target": row["pushup_count"]},
            {"name": "Plank", "target": row["plank_time"]},
            {"name": "Crunches", "target": row["crunches_count"]},
            {"name": "Squats", "target": row["squat_count"]},
            {"name": "Cobra Stretch", "target": row["cobra_stretch_time"]}
        ]
    finally:
        close_connection(connection, cursor)
"""

def get_workout_plan(plan_id):
    connection = get_db_connection()
    if not connection:
        return []

    try:
        cursor = connection.cursor()

        # Fetch plan data
        cursor.execute("SELECT * FROM workout_plan WHERE plan_id = ?", (plan_id,))
        plan = cursor.fetchone()
        if not plan:
            return []

        # Fetch workouts
        cursor.execute("""
            SELECT workout_id, workout_name, video_url
            FROM workout
            ORDER BY workout_id
        """)
        workouts = cursor.fetchall()

        workout_plan = []

        for w in workouts:
            workout = dict(w)

            wid = workout["workout_id"]

            # 🔑 ID-based mapping (SAFE)
            if wid == 1:      # Jumping Jacks
                target = plan["jumpingjack_count"]
            elif wid == 2:    # Push Ups
                target = plan["pushup_count"]
            elif wid == 3:    # Plank
                target = plan["plank_time"]
            elif wid == 4:    # Crunches
                target = plan["crunches_count"]
            elif wid == 5:    # Squats
                target = plan["squat_count"]
            elif wid == 6:    # Cobra Stretch
                target = plan["cobra_stretch_time"]
            else:
                target = 0

            workout_plan.append({
                "workout_id": wid,
                "name": workout["workout_name"],
                "video_path": workout["video_url"],
                "target_reps": target
            })

        return workout_plan

    finally:
        close_connection(connection, cursor)




# =====================================================
# WORKOUT SESSION
# =====================================================

def save_workout_session(trainee_id, session_data):
    connection = get_db_connection()
    if not connection:
        return False, "Database connection failed"

    try:
        cursor = connection.cursor()
        cols = ["trainee_id"] + WORKOUT_COLUMNS
        placeholders = ["?"] * len(cols)

        query = f"INSERT INTO workout_session ({', '.join(cols)}) VALUES ({', '.join(placeholders)})"
        params = [trainee_id] + [session_data.get(c, 0) for c in WORKOUT_COLUMNS]

        cursor.execute(query, params)
        connection.commit()
        return True, "Session saved"
    except sqlite3.Error as e:
        return False, str(e)
    finally:
        close_connection(connection, cursor)


def get_latest_session_status(trainee_id):
    connection = get_db_connection()
    if not connection:
        return None

    try:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT * FROM workout_session
            WHERE trainee_id = ?
            ORDER BY session_id DESC LIMIT 1
        """, (trainee_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        close_connection(connection, cursor)

# =====================================================
# PROFILE
# =====================================================

def get_trainee(trainee_id):
    connection = get_db_connection()
    if not connection:
        return None

    try:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM trainee WHERE trainee_id = ?", (trainee_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        close_connection(connection, cursor)


def update_trainee(trainee_id, **kwargs):
    if not kwargs:
        return False, "No fields to update"

    connection = get_db_connection()
    if not connection:
        return False, "Database connection failed"

    try:
        cursor = connection.cursor()
        fields = [f"{k}=?" for k in kwargs]
        values = list(kwargs.values()) + [trainee_id]

        query = f"UPDATE trainee SET {', '.join(fields)} WHERE trainee_id = ?"
        cursor.execute(query, values)
        connection.commit()
        return True, "Profile updated"
    finally:
        close_connection(connection, cursor)
        
# =====================================================
# ANALYTICS (GLOBAL SHARED INSTANCE)
# =====================================================

class WorkoutSessionStats:
    def __init__(self, exercise_name, reps_completed, correct_reps, wrong_reps, duration):
        self.exercise_name = exercise_name
        self.reps_completed = reps_completed
        self.correct_reps = correct_reps
        self.wrong_reps = wrong_reps
        self.duration = duration


class SessionAnalytics:
    def __init__(self):
        self.sessions = []
        self.total_sessions = 0

    def load_sessions(self, trainee_id):
        connection = get_db_connection()
        if not connection:
            return

        try:
            cursor = connection.cursor()
            cursor.execute("""
                SELECT * FROM workout_session
                WHERE trainee_id = ?
                ORDER BY session_id DESC
            """, (trainee_id,))
            rows = cursor.fetchall()

            self.sessions.clear()
            self.total_sessions = len(rows)

            for row in rows:
                exercises = [
                    ("Push-up", "pushup_crt", "pushup_wrg"),
                    ("Jumping Jack", "jumpingjack_crt", "jumpingjack_wrg"),
                    ("Squat", "squat_crt", "squat_wrg"),
                    ("Crunches", "crunches_crt", "crunches_wrg")
                ]

                for name, crt_col, wrg_col in exercises:
                    crt = row[crt_col] or 0
                    wrg = row[wrg_col] or 0
                    if crt or wrg:
                        self.sessions.append(
                            WorkoutSessionStats(
                                name, crt + wrg, crt, wrg, 0
                            )
                        )

                time_exercises = [
                    ("Plank", "plank_time"),
                    ("Cobra Stretch", "cobrastretch_time")
                ]

                for name, col in time_exercises:
                    t = row[col] or 0
                    if t:
                        self.sessions.append(
                            WorkoutSessionStats(name, 0, 0, 0, t)
                        )

        finally:
            close_connection(connection, cursor)


# ✅ THIS LINE FIXES YOUR ERROR
session_analytics = SessionAnalytics()
