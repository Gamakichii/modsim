import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3


# Database setup
def create_database():
    conn = sqlite3.connect('gym_simulation.db')
    c = conn.cursor()

    # Create Tables
    c.execute('''CREATE TABLE IF NOT EXISTS rooms (room_id TEXT, capacity INTEGER, room_type TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS trainers (trainer_id INTEGER PRIMARY KEY, name TEXT, expertise TEXT, available_times TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS students (student_id INTEGER PRIMARY KEY, name TEXT, training_preference TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS assignments (student_id INTEGER, trainer_id INTEGER, time_slot TEXT, FOREIGN KEY(student_id) REFERENCES students(student_id), FOREIGN KEY(trainer_id) REFERENCES trainers(trainer_id))''')
    
    conn.commit()
    conn.close()


# GUI Application
class GymSimulatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Gym Facility Management Tool with Automatic Trainer Assignment")
        
        # Initialize database
        create_database()

        # Add Room Section
        tk.Label(root, text="Room ID").grid(row=0, column=0)
        self.room_id_entry = tk.Entry(root)
        self.room_id_entry.grid(row=0, column=1)

        tk.Label(root, text="Capacity").grid(row=0, column=2)
        self.room_capacity_entry = tk.Entry(root)
        self.room_capacity_entry.grid(row=0, column=3)

        tk.Label(root, text="Room Type").grid(row=0, column=4)
        self.room_type_combo = ttk.Combobox(root, values=["workout room", "yoga studio", "weight room"])
        self.room_type_combo.grid(row=0, column=5)
        self.room_type_combo.set("workout room")

        tk.Button(root, text="Add Room", command=self.add_room).grid(row=0, column=6)

        # Add Trainer Section
        tk.Label(root, text="Trainer Name").grid(row=1, column=0)
        self.trainer_name_entry = tk.Entry(root)
        self.trainer_name_entry.grid(row=1, column=1)

        tk.Label(root, text="Expertise").grid(row=1, column=2)
        self.trainer_expertise_entry = tk.Entry(root)
        self.trainer_expertise_entry.grid(row=1, column=3)

        tk.Label(root, text="Available Times").grid(row=1, column=4)
        self.trainer_times_combo = ttk.Combobox(root, values=["6:00 AM", "7:00 AM", "8:00 AM", "9:00 AM", "10:00 AM"])
        self.trainer_times_combo.grid(row=1, column=5)
        self.trainer_times_combo.set("6:00 AM")

        tk.Button(root, text="Add Trainer", command=self.add_trainer).grid(row=1, column=6)

        # Add Student Section
        tk.Label(root, text="Student Name").grid(row=2, column=0)
        self.student_name_entry = tk.Entry(root)
        self.student_name_entry.grid(row=2, column=1)

        tk.Label(root, text="Training Preference").grid(row=2, column=2)
        self.student_training_combo = ttk.Combobox(root, values=["Yoga", "Weightlifting", "HIIT"])
        self.student_training_combo.grid(row=2, column=3)
        self.student_training_combo.set("Yoga")

        tk.Button(root, text="Add Student", command=self.add_student).grid(row=2, column=6)

        # Assign Button
        tk.Button(root, text="Assign Students to Trainers", command=self.assign_students).grid(row=3, column=1)

        # Output Area
        self.output_text = tk.Text(root, height=10, width=100)
        self.output_text.grid(row=4, column=0, columnspan=7)

    # Add Room to Database
    def add_room(self):
        room_id = self.room_id_entry.get()
        capacity = self.room_capacity_entry.get()
        room_type = self.room_type_combo.get()

        if not room_id or not capacity.isdigit():
            messagebox.showerror("Input Error", "Please enter valid Room ID and Capacity.")
            return

        conn = sqlite3.connect('gym_simulation.db')
        c = conn.cursor()
        c.execute("INSERT INTO rooms (room_id, capacity, room_type) VALUES (?, ?, ?)", (room_id, int(capacity), room_type))
        conn.commit()
        conn.close()

        self.update_output(f"Added Room: {room_id}, Capacity: {capacity}, Type: {room_type}")

    # Add Trainer to Database
    def add_trainer(self):
        name = self.trainer_name_entry.get()
        expertise = self.trainer_expertise_entry.get()
        available_times = self.trainer_times_combo.get()

        if not name or not expertise or not available_times:
            messagebox.showerror("Input Error", "Please enter all trainer details.")
            return

        conn = sqlite3.connect('gym_simulation.db')
        c = conn.cursor()
        c.execute("INSERT INTO trainers (name, expertise, available_times) VALUES (?, ?, ?)", (name, expertise, available_times))
        conn.commit()
        conn.close()

        self.update_output(f"Added Trainer: {name}, Expertise: {expertise}, Available Time: {available_times}")

    # Add Student to Database
    def add_student(self):
        name = self.student_name_entry.get()
        training_preference = self.student_training_combo.get()

        if not name or not training_preference:
            messagebox.showerror("Input Error", "Please enter all student details.")
            return

        conn = sqlite3.connect('gym_simulation.db')
        c = conn.cursor()
        c.execute("INSERT INTO students (name, training_preference) VALUES (?, ?)", (name, training_preference))
        conn.commit()
        conn.close()

        self.update_output(f"Added Student: {name}, Training Preference: {training_preference}")

    # Assign Students to Trainers Automatically
    def assign_students(self):
        conn = sqlite3.connect('gym_simulation.db')
        c = conn.cursor()

        # Fetch all students
        c.execute("SELECT student_id, name, training_preference FROM students")
        students = c.fetchall()

        # Fetch all trainers and their availability
        c.execute("SELECT trainer_id, name, expertise, available_times FROM trainers")
        trainers = c.fetchall()

        for student in students:
            student_id, student_name, training_preference = student
            assigned = False

            for trainer in trainers:
                trainer_id, trainer_name, expertise, available_time = trainer

                # Check if the trainer's expertise matches the student's preference
                if training_preference in expertise:
                    # Assign student to trainer
                    c.execute("INSERT INTO assignments (student_id, trainer_id, time_slot) VALUES (?, ?, ?)",
                              (student_id, trainer_id, available_time))
                    conn.commit()
                    self.update_output(f"Assigned {student_name} to {trainer_name} at {available_time}")
                    assigned = True
                    break

            if not assigned:
                self.update_output(f"No available trainer for {student_name} with preference {training_preference}")

        conn.close()

    # Update output
    def update_output(self, message):
        self.output_text.insert(tk.END, message + "\n")


# Main application
if __name__ == "__main__":
    root = tk.Tk()
    app = GymSimulatorGUI(root)
    root.mainloop()
