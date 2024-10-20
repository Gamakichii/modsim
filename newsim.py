import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import random
from datetime import datetime, timedelta

# Database setup function
def create_database():
    conn = sqlite3.connect('gym_simulation.db')
    c = conn.cursor()

    # Create Tables
    c.execute('''CREATE TABLE IF NOT EXISTS rooms (room_id TEXT PRIMARY KEY, capacity INTEGER, room_type TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS trainers (trainer_id INTEGER PRIMARY KEY, name TEXT, expertise TEXT, available_days TEXT, start_time TEXT, end_time TEXT, room_id TEXT, FOREIGN KEY(room_id) REFERENCES rooms(room_id))''')
    c.execute('''CREATE TABLE IF NOT EXISTS students (student_id INTEGER PRIMARY KEY, name TEXT, training_preference TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS student_details (student_id INTEGER PRIMARY KEY, height INTEGER, weight INTEGER, age INTEGER, activity_level INTEGER, occupation_status TEXT, goal TEXT, FOREIGN KEY(student_id) REFERENCES students(student_id))''')
    c.execute('''CREATE TABLE IF NOT EXISTS assignments (student_id INTEGER, trainer_id INTEGER, time_slot TEXT, date TEXT, FOREIGN KEY(student_id) REFERENCES students(student_id), FOREIGN KEY(trainer_id) REFERENCES trainers(trainer_id))''')
    c.execute('''CREATE TABLE IF NOT EXISTS workouts (student_id INTEGER, date TEXT, exercises TEXT, FOREIGN KEY(student_id) REFERENCES students(student_id))''')

    conn.commit()
    conn.close()

# GUI Application
class GymSimulatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Gym Facility Management Tool")
        
        # Set window size
        self.root.geometry("900x600")
        self.root.resizable(True, True)

        # Initialize database
        create_database()

        # Main Frame
        main_frame = ttk.Frame(root, padding=10)
        main_frame.grid(row=0, column=0, sticky="nsew")

        # Configure rows and columns to be responsive
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)

        # Frame for Admin Section
        self.admin_frame = ttk.LabelFrame(main_frame, text="Add & Manage Gym Resources", padding=(10, 10))
        self.admin_frame.grid(row=0, column=0, sticky='ew', padx=10, pady=10)

        # Room Section
        self.add_room_section()

        # Trainer Section
        self.add_trainer_section()

        # Student Section
        self.student_frame = ttk.LabelFrame(main_frame, text="Add Student", padding=(10, 10))
        self.student_frame.grid(row=1, column=0, sticky='ew', padx=10, pady=10)
        self.add_student_section(self.student_frame)

        # Progress Monitoring Section
        self.progress_frame = ttk.LabelFrame(main_frame, text="View Progress", padding=(10, 10))
        self.progress_frame.grid(row=2, column=0, sticky='ew', padx=10, pady=10)
        self.add_progress_section(self.progress_frame)  # Pass the parent frame

        # Output Area
        self.output_text = tk.Text(main_frame, height=15, width=100, wrap=tk.WORD)
        self.output_text.grid(row=3, column=0, columnspan=1, padx=10, pady=10, sticky='ew')

    def add_room_section(self):
        """ Adds the room management section. """
        # Room ID Input
        ttk.Label(self.admin_frame, text="Room ID").grid(row=0, column=0, padx=5, pady=5)
        self.room_id_entry = ttk.Entry(self.admin_frame, width=27)  # Allow admin to input the room ID
        self.room_id_entry.grid(row=0, column=1, padx=5, pady=5)

        # Room Capacity Input
        ttk.Label(self.admin_frame, text="Capacity").grid(row=0, column=2, padx=5, pady=5)
        self.room_capacity_entry = ttk.Entry(self.admin_frame, width=10)
        self.room_capacity_entry.grid(row=0, column=3, padx=5, pady=5)

        # Room Type Selection
        ttk.Label(self.admin_frame, text="Room Type").grid(row=0, column=4, padx=5, pady=5)
        self.room_type_combo = ttk.Combobox(self.admin_frame, values=["Workout Room", "Yoga Studio", "Weight Room"], state='readonly', width=27)
        self.room_type_combo.grid(row=0, column=5, padx=5, pady=5)
        self.room_type_combo.set("Workout Room")

        # Button to Add Room
        ttk.Button(self.admin_frame, text="Add Room", command=self.add_room).grid(row=0, column=6, padx=5, pady=5)

    def add_trainer_section(self):
        """ Adds the trainer management section. """
        ttk.Label(self.admin_frame, text="Trainer Name").grid(row=1, column=0, padx=5, pady=5)
        self.trainer_name_entry = ttk.Entry(self.admin_frame, width=27)
        self.trainer_name_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(self.admin_frame, text="Expertise").grid(row=1, column=2, padx=5, pady=5)
        self.trainer_expertise_combo = ttk.Combobox(self.admin_frame, values=["Fitness", "Yoga", "HIIT", "Weightlifting", "Pilates"], state='readonly', width=27)
        self.trainer_expertise_combo.grid(row=1, column=3, padx=5, pady=5)
        self.trainer_expertise_combo.set("Select Expertise")

        # Available Days Checkboxes
        ttk.Label(self.admin_frame, text="Available Days").grid(row=1, column=4, padx=5, pady=5)
        self.available_days_frame = ttk.Frame(self.admin_frame)
        self.available_days_frame.grid(row=1, column=5, padx=5, pady=5)

        self.days_var = {day: tk.BooleanVar() for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]}
        for day, var in self.days_var.items():
            ttk.Checkbutton(self.available_days_frame, text=day, variable=var).pack(side=tk.LEFT)

        ttk.Label(self.admin_frame, text="Start Time").grid(row=1, column=6, padx=5, pady=5)
        self.start_time_combo = ttk.Combobox(self.admin_frame, values=[f"{hour:02}:00" for hour in range(24)], state='readonly', width=10)  # 00:00 to 23:00
        self.start_time_combo.grid(row=1, column=7, padx=5, pady=5)
        self.start_time_combo.set("Select Start Time")

        ttk.Label(self.admin_frame, text="End Time").grid(row=1, column=8, padx=5, pady=5)
        self.end_time_combo = ttk.Combobox(self.admin_frame, values=[f"{hour:02}:00" for hour in range(24)], state='readonly', width=10)  # 00:00 to 23:00
        self.end_time_combo.grid(row=1, column=9, padx=5, pady=5)
        self.end_time_combo.set("Select End Time")

        ttk.Label(self.admin_frame, text="Room").grid(row=1, column=10, padx=5, pady=5)

        # Room selection combobox populated from the database
        self.trainer_room_combo = ttk.Combobox(self.admin_frame, values=self.fetch_room_ids(), state='readonly', width=27)  # Populate with existing room IDs
        self.trainer_room_combo.grid(row=1, column=11, padx=5, pady=5)
        self.trainer_room_combo.set("Select Room ID")

        ttk.Button(self.admin_frame, text="Add Trainer", command=self.add_trainer).grid(row=1, column=12, padx=5, pady=5)

    def add_student_section(self, parent):
        """ Adds the student management section. """
        ttk.Label(self.student_frame, text="Student Name").grid(row=0, column=0, padx=5, pady=5)
        self.student_name_entry = ttk.Entry(self.student_frame, width=27)
        self.student_name_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(self.student_frame, text="Training Preference").grid(row=0, column=2, padx=5, pady=5)
        self.student_training_combo = ttk.Combobox(self.student_frame, values=["Yoga", "Weightlifting", "HIIT"], state='readonly', width=27)
        self.student_training_combo.grid(row=0, column=3, padx=5, pady=5)
        self.student_training_combo.set("Yoga")

        ttk.Label(self.student_frame, text="Age").grid(row=1, column=0, padx=5, pady=5)
        self.age_entry = ttk.Entry(self.student_frame, width=10)
        self.age_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(self.student_frame, text="Height (cm)").grid(row=1, column=2, padx=5, pady=5)
        self.height_entry = ttk.Entry(self.student_frame, width=10)
        self.height_entry.grid(row=1, column=3, padx=5, pady=5)

        ttk.Label(self.student_frame, text="Weight (kg)").grid(row=1, column=4, padx=5, pady=5)
        self.weight_entry = ttk.Entry(self.student_frame, width=10)
        self.weight_entry.grid(row=1, column=5, padx=5, pady=5)

        ttk.Label(self.student_frame, text="Activity Level (1-10)").grid(row=2, column=0, padx=5, pady=5)
        self.activity_level_entry = ttk.Entry(self.student_frame, width=10)
        self.activity_level_entry.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(self.student_frame, text="Occupation Status").grid(row=2, column=2, padx=5, pady=5)
        self.occupation_entry = ttk.Entry(self.student_frame, width=27)
        self.occupation_entry.grid(row=2, column=3, padx=5, pady=5)

        ttk.Label(self.student_frame, text="Goal").grid(row=2, column=4, padx=5, pady=5)
        self.goal_entry = ttk.Entry(self.student_frame, width=27)
        self.goal_entry.grid(row=2, column=5, padx=5, pady=5)

        ttk.Button(self.student_frame, text="Add Student", command=self.add_student).grid(row=3, column=2, columnspan=2, padx=5, pady=5)
        ttk.Button(self.student_frame, text="Simulate Assignments", command=self.simulate_assignments).grid(row=4, column=2, columnspan=1, padx=5, pady=5)
        ttk.Button(self.student_frame, text="Simulate Progress", command=self.simulate_progress).grid(row=4, column=3, columnspan=1, padx=5, pady=5)

    def add_progress_section(self, parent):
        """ Adds the progress monitoring section. """
        ttk.Label(self.progress_frame, text="Select Time Period").grid(row=0, column=0, padx=5, pady=5)
        self.period_combo = ttk.Combobox(self.progress_frame, values=["Daily", "Weekly", "Monthly", "Annually"])
        self.period_combo.set("Select Period")
        self.period_combo.grid(row=0, column=1, padx=5, pady=5)

        ttk.Button(self.progress_frame, text="View Progress", command=self.view_progress).grid(row=0, column=2, padx=5, pady=5)

    def fetch_room_ids(self):
        """ Fetches existing room IDs for pre-selection. """
        conn = sqlite3.connect('gym_simulation.db')
        c = conn.cursor()
        c.execute("SELECT room_id FROM rooms")
        room_ids = [room[0] for room in c.fetchall()]
        conn.close()
        return room_ids if room_ids else ["Room 1", "Room 2", "Room 3"]  # Default options if empty

    def add_room(self):
        """ Adds a room to the database with user input. """
        room_id = self.room_id_entry.get()
        capacity = self.room_capacity_entry.get()
        room_type = self.room_type_combo.get()

        if not room_id or not capacity.isdigit() or not room_type:
            messagebox.showerror("Input Error", "Please enter valid Room ID, Capacity, and Room Type.")
            return

        conn = sqlite3.connect('gym_simulation.db')
        c = conn.cursor()
        c.execute("INSERT OR REPLACE INTO rooms (room_id, capacity, room_type) VALUES (?, ?, ?)", (room_id, int(capacity), room_type))
        conn.commit()
        conn.close()

        self.update_output(f"Added/Updated Room: {room_id}, Capacity: {capacity}, Type: {room_type}")

    def add_trainer(self):
        """ Adds a trainer to the database with user input. """
        name = self.trainer_name_entry.get()
        expertise = self.trainer_expertise_combo.get()
        available_days = ','.join([day for day, var in self.days_var.items() if var.get()])
        start_time = self.start_time_combo.get()
        end_time = self.end_time_combo.get()
        room_id = self.trainer_room_combo.get()

        if not name or not expertise or not available_days or not start_time or not end_time or not room_id:
            messagebox.showerror("Input Error", "Please enter all trainer details.")
            return

        conn = sqlite3.connect('gym_simulation.db')
        c = conn.cursor()
        c.execute("INSERT INTO trainers (name, expertise, available_days, start_time, end_time, room_id) VALUES (?, ?, ?, ?, ?, ?)", 
                    (name, expertise, available_days, start_time, end_time, room_id))
        conn.commit()
        conn.close()

        self.update_output(f"Added Trainer: {name}, Expertise: {expertise}, Available Days: {available_days}, Start: {start_time}, End: {end_time}, Room: {room_id}")

    def add_student(self):
        """ Adds a student to the database. """
        name = self.student_name_entry.get()
        training_preference = self.student_training_combo.get()
        age = self.age_entry.get()
        height = self.height_entry.get()
        weight = self.weight_entry.get()
        activity_level = self.activity_level_entry.get()
        occupation_status = self.occupation_entry.get()
        goal = self.goal_entry.get()

        if not name or not training_preference or not age.isdigit() or not height.isdigit() or not weight.isdigit() or not activity_level.isdigit():
            messagebox.showerror("Input Error", "Please enter valid student details.")
            return

        conn = sqlite3.connect('gym_simulation.db')
        c = conn.cursor()
        c.execute("INSERT INTO students (name, training_preference) VALUES (?, ?)", (name, training_preference))
        conn.commit()
        student_id = c.lastrowid

        # Store user details
        c.execute("INSERT INTO student_details (student_id, height, weight, age, activity_level, occupation_status, goal) VALUES (?, ?, ?, ?, ?, ?, ?)",
                  (student_id, int(height), int(weight), int(age), int(activity_level), occupation_status, goal))
        conn.commit()
        conn.close()

        self.update_output(f"Added Student: {name}")

    def simulate_assignments(self):
        """ Simulates the assignment of students to trainers based on preferences. """
        conn = sqlite3.connect('gym_simulation.db')
        c = conn.cursor()

        # Fetch all students
        c.execute("SELECT student_id, name, training_preference FROM students")
        students = c.fetchall()

        # Fetch all trainers and their availability
        c.execute("SELECT trainer_id, name, expertise, available_days, start_time, end_time, room_id FROM trainers")
        trainers = c.fetchall()

        for student in students:
            student_id, student_name, training_preference = student
            assigned = False

            for trainer in trainers:
                trainer_id, trainer_name, expertise, available_days, start_time, end_time, room_id = trainer

                # Check if the trainer's expertise matches the student's preference
                if training_preference in expertise:
                    # Check if the trainer is available on the selected day
                    today = datetime.now().strftime("%A")  # Get today's day of the week
                    if today in available_days.split(','):
                        # Check time availability
                        current_time = datetime.now().strftime("%H:%M")
                        if start_time <= current_time <= end_time:
                            # Assign student to trainer
                            c.execute("INSERT INTO assignments (student_id, trainer_id, time_slot, date) VALUES (?, ?, ?, ?)",
                                      (student_id, trainer_id, current_time, datetime.now().strftime("%Y-%m-%d")))
                            conn.commit()
                            self.update_output(f"Assigned {student_name} to {trainer_name} in {room_id} at {current_time} on {datetime.now().strftime('%Y-%m-%d')}")
                            assigned = True
                            break

            if not assigned:
                self.update_output(f"No available trainer for {student_name} with preference {training_preference}")

        conn.close()

    def simulate_progress(self):
        """ Simulates the progress of each student based on their assignments. """
        conn = sqlite3.connect('gym_simulation.db')
        c = conn.cursor()

        # Fetch all students' details
        c.execute("SELECT sd.student_id, s.name, sd.weight, sd.goal, sd.activity_level FROM student_details sd JOIN students s ON sd.student_id = s.student_id")
        students = c.fetchall()

        for student in students:
            student_id, student_name, weight, goal, activity_level = student
            weight_change = 0

            # Simulate weight change based on activity level and goal
            if goal.lower() == "weight loss":
                weight_change = -random.uniform(0.1, 2) * (int(activity_level) / 10)  # Simulate weight loss based on activity level
            elif goal.lower() == "muscle gain":
                weight_change = random.uniform(0.1, 1) * (int(activity_level) / 10)  # Simulate weight gain based on activity level

            # Update the weight
            new_weight = round(weight + weight_change, 2)
            c.execute("UPDATE student_details SET weight = ? WHERE student_id = ?", (new_weight, student_id))
            conn.commit()

            self.update_output(f"Progress updated for {student_name}: New Weight = {new_weight} kg.")

        conn.close()

    def view_progress(self):
        """ Fetches and displays the progress of students based on the selected period. """
        period = self.period_combo.get()
        conn = sqlite3.connect('gym_simulation.db')
        c = conn.cursor()

        # Get today's date
        today = datetime.now()

        # Initialize a date range based on the selected period
        if period == "Daily":
            start_date = today
            end_date = today
        elif period == "Weekly":
            start_date = today - timedelta(weeks=1)
            end_date = today
        elif period == "Monthly":
            start_date = today - timedelta(days=30)
            end_date = today
        elif period == "Annually":
            start_date = today - timedelta(days=365)
            end_date = today
        else:
            messagebox.showerror("Input Error", "Please select a valid period.")
            return

        # Fetch workout data based on the selected period
        c.execute("SELECT wd.student_id, wd.date, wd.exercises FROM workouts wd WHERE wd.date BETWEEN ? AND ?", 
                   (start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")))
        workouts = c.fetchall()

        if not workouts:
            self.update_output("No workouts recorded in this period.")
            return

        # Output the exercises performed by each student
        for workout in workouts:
            student_id, date, exercises = workout
            self.update_output(f"Student ID: {student_id}, Date: {date}, Exercises: {exercises}")

        conn.close()

    def update_output(self, message):
        """ Updates the output text area with new messages. """
        self.output_text.insert(tk.END, message + "\n")
        self.output_text.see(tk.END)  # Scroll to the end of the output text area

# Main application
if __name__ == "__main__":
    root = tk.Tk()
    app = GymSimulatorGUI(root)
    root.mainloop()

