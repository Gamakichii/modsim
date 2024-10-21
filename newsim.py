import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import sqlite3
import random
from datetime import datetime

# Database setup function
def create_database():
    conn = sqlite3.connect('gym_simulation.db')
    c = conn.cursor()

    # Drop existing tables (resetting structure)
    c.execute("DROP TABLE IF EXISTS progress")
    c.execute("DROP TABLE IF EXISTS members")
    c.execute("DROP TABLE IF EXISTS trainers")

    # Create tables
    c.execute('''CREATE TABLE IF NOT EXISTS trainers (
                    trainer_id INTEGER PRIMARY KEY,
                    name TEXT,
                    expertise TEXT,
                    available_days TEXT)''')

    c.execute('''CREATE TABLE IF NOT EXISTS members (
                    member_id INTEGER PRIMARY KEY,
                    name TEXT,
                    birthday TEXT,
                    height INTEGER,
                    weight REAL,
                    activity_level INTEGER,
                    goal TEXT,
                    protein_needed REAL,
                    carb_needed REAL,
                    fiber_needed REAL,
                    trainer_id INTEGER,
                    FOREIGN KEY(trainer_id) REFERENCES trainers(trainer_id))''')

    c.execute('''CREATE TABLE IF NOT EXISTS progress (
                    member_id INTEGER,
                    date TEXT,
                    weight REAL,
                    FOREIGN KEY(member_id) REFERENCES members(member_id))''')

    conn.commit()
    conn.close()

# Main GUI Application Class
class GymManagementGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Gym Management Tool")
        self.root.geometry("900x600")
        self.root.configure(bg='#f5f5f5')

        self.create_goal_options = {
            "Fitness": ["Weight Loss", "Muscle Gain", "General Health"],
            "Yoga": ["Flexibility Improvement", "Stress Relief", "Mindfulness"],
            "HIIT": ["Fat Loss", "Endurance", "Strength"],
            "Weightlifting": ["Muscle Gain", "Strength Building", "Powerlifting"],
            "Pilates": ["Core Strength", "Flexibility", "Rehabilitation"]
        }

        self.trainer_names = ["John Doe", "Jane Smith", "Jim Brown", "Jake White", "Lisa Green", "Tom Black"]
        self.expertise_types = list(self.create_goal_options.keys())
        self.available_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

        create_database()
        self.create_dashboard()

        # Track whether unassigned members have been assigned
        self.unassigned_assigned = False

    def create_dashboard(self):
        self.clear_main_frame()
        dashboard_frame = ttk.Frame(self.root, padding=10)
        dashboard_frame.grid(row=0, column=0, sticky="nsew")

        # Trainer Management Section
        self.trainer_frame = ttk.LabelFrame(dashboard_frame, text="Manage Trainers", padding=(10, 10))
        self.trainer_frame.grid(row=0, column=0, sticky='ew', padx=10, pady=10)
        self.add_trainer_section()

        # Member Management Section
        self.member_frame = ttk.LabelFrame(dashboard_frame, text="Manage Members", padding=(10, 10))
        self.member_frame.grid(row=1, column=0, sticky='ew', padx=10, pady=10)
        self.add_member_section()

        # Progress Section
        self.progress_frame = ttk.LabelFrame(dashboard_frame, text="Simulate Progress", padding=(10, 10))
        self.progress_frame.grid(row=2, column=0, sticky='ew', padx=10, pady=10)
        self.add_progress_section()

        # View Progress Section
        self.view_progress_frame = ttk.LabelFrame(dashboard_frame, text="View Progress", padding=(10, 10))
        self.view_progress_frame.grid(row=3, column=0, sticky='ew', padx=10, pady=10)
        self.add_view_progress_section()

        # Buttons to View All Trainers and Members
        ttk.Button(dashboard_frame, text="View All Trainers", command=self.view_all_trainers).grid(row=4, column=0, padx=10, pady=10)
        ttk.Button(dashboard_frame, text="View All Members", command=self.view_all_members).grid(row=5, column=0, padx=10, pady=10)

        # Auto Add Buttons
        ttk.Button(dashboard_frame, text="Auto Add Trainers", command=self.auto_add_trainers).grid(row=6, column=0, padx=10, pady=10)
        ttk.Button(dashboard_frame, text="Auto Add Members", command=self.auto_add_members).grid(row=7, column=0, padx=10, pady=10)

    def clear_main_frame(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def add_trainer_section(self):
        ttk.Label(self.trainer_frame, text="Trainer Name:").grid(row=0, column=0, padx=5, pady=5)
        self.trainer_name_entry = ttk.Entry(self.trainer_frame)
        self.trainer_name_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(self.trainer_frame, text="Expertise:").grid(row=0, column=2, padx=5, pady=5)
        self.trainer_expertise_combo = ttk.Combobox(self.trainer_frame, values=self.expertise_types)
        self.trainer_expertise_combo.grid(row=0, column=3, padx=5, pady=5)
        self.trainer_expertise_combo.bind("<<ComboboxSelected>>", self.update_goals)

        ttk.Label(self.trainer_frame, text="Available Days:").grid(row=1, column=0, padx=5, pady=5)
        self.available_days_frame = ttk.Frame(self.trainer_frame)
        self.available_days_frame.grid(row=1, column=1, columnspan=3)

        self.days_var = {day: tk.BooleanVar() for day in self.available_days}
        for day, var in self.days_var.items():
            ttk.Checkbutton(self.available_days_frame, text=day, variable=var).pack(side=tk.LEFT)

        ttk.Button(self.trainer_frame, text="Add Trainer", command=self.add_trainer).grid(row=2, column=0, columnspan=4, padx=5, pady=5)

    def add_member_section(self):
        ttk.Label(self.member_frame, text="Member Name:").grid(row=0, column=0, padx=5, pady=5)
        self.member_name_entry = ttk.Entry(self.member_frame)
        self.member_name_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(self.member_frame, text="Birthday:").grid(row=0, column=2, padx=5, pady=5)
        self.member_birthday_entry = DateEntry(self.member_frame)
        self.member_birthday_entry.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(self.member_frame, text="Height (cm):").grid(row=1, column=0, padx=5, pady=5)
        self.member_height_entry = ttk.Entry(self.member_frame)
        self.member_height_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(self.member_frame, text="Weight (kg):").grid(row=1, column=2, padx=5, pady=5)
        self.member_weight_entry = ttk.Entry(self.member_frame)
        self.member_weight_entry.grid(row=1, column=3, padx=5, pady=5)

        ttk.Label(self.member_frame, text="Activity Level (1-10):").grid(row=2, column=0, padx=5, pady=5)
        self.activity_level_entry = ttk.Entry(self.member_frame)
        self.activity_level_entry.grid(row=2, column=1, padx=5, pady=5)

        # Move Trainer's Expertise dropdown before the Goal dropdown
        ttk.Label(self.member_frame, text="Trainer Expertise:").grid(row=3, column=0, padx=5, pady=5)
        self.trainer_expertise_member_combo = ttk.Combobox(self.member_frame, values=self.expertise_types)
        self.trainer_expertise_member_combo.grid(row=3, column=1, padx=5, pady=5)
        self.trainer_expertise_member_combo.bind("<<ComboboxSelected>>", self.update_goals_member)

        ttk.Label(self.member_frame, text="Goal:").grid(row=4, column=0, padx=5, pady=5)
        self.member_goal_combo = ttk.Combobox(self.member_frame, state='readonly')
        self.member_goal_combo.grid(row=4, column=1, columnspan=2, padx=5, pady=5)

        ttk.Button(self.member_frame, text="Add Member", command=self.add_member).grid(row=5, column=0, columnspan=3, padx=5, pady=5)
        ttk.Button(self.member_frame, text="Assign Unassigned Members", command=self.assign_unassigned_members).grid(row=6, column=0, columnspan=3, padx=5, pady=5)

    def add_progress_section(self):
        ttk.Label(self.progress_frame, text="Days Passed:").grid(row=0, column=0, padx=5, pady=5)
        self.days_passed_entry = ttk.Entry(self.progress_frame)
        self.days_passed_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Button(self.progress_frame, text="Simulate Progress", command=self.simulate_progress).grid(row=1, column=0, columnspan=2, padx=5, pady=5)

    def add_view_progress_section(self):
        ttk.Label(self.view_progress_frame, text="Member ID:").grid(row=0, column=0, padx=5, pady=5)
        self.member_id_entry = ttk.Entry(self.view_progress_frame)
        self.member_id_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Button(self.view_progress_frame, text="View Progress", command=self.view_progress).grid(row=1, column=0, columnspan=2, padx=5, pady=5)

    def update_goals(self, event):
        expertise = self.trainer_expertise_combo.get()
        if expertise in self.create_goal_options:
            goals = self.create_goal_options[expertise]
            self.trainer_goal_combo['values'] = goals
            self.trainer_goal_combo.current(0)

    def update_goals_member(self, event):
        expertise = self.trainer_expertise_member_combo.get()
        if expertise in self.create_goal_options:
            goals = self.create_goal_options[expertise]
            self.member_goal_combo['values'] = goals
            self.member_goal_combo.current(0)

    def view_all_trainers(self):
        conn = sqlite3.connect('gym_simulation.db')
        c = conn.cursor()
        c.execute("SELECT * FROM trainers")
        trainers = c.fetchall()
        conn.close()
        
        trainer_list = '\n'.join([f"{trainer[0]}: {trainer[1]}, Expertise: {trainer[2]}, Days: {trainer[3]}" for trainer in trainers])
        messagebox.showinfo("All Trainers", trainer_list or "No trainers found.")

    def view_all_members(self):
        conn = sqlite3.connect('gym_simulation.db')
        c = conn.cursor()
        c.execute("SELECT * FROM members")
        members = c.fetchall()
        conn.close()
        
        member_list = '\n'.join([f"{member[0]}: {member[1]}, Goal: {member[6]}, Trainer ID: {member[10]}" for member in members])
        messagebox.showinfo("All Members", member_list or "No members found.")

    def auto_add_trainers(self):
        for name in self.trainer_names:
            self.trainer_name_entry.delete(0, tk.END)
            self.trainer_name_entry.insert(0, name)
            expertise = random.choice(self.expertise_types)
            self.trainer_expertise_combo.set(expertise)

            # Set available days randomly for the auto-generated trainer
            for day, var in self.days_var.items():
                var.set(random.choice([True, False]))  # Randomly select available days

            # Check if all required fields are filled
            if self.trainer_name_entry.get() and expertise and any(var.get() for var in self.days_var.values()):
                self.add_trainer()  # Add the trainer if all fields are filled
            else:
                messagebox.showerror("Error", "Please fill all fields.")

        messagebox.showinfo("Success", "Auto-added trainers successfully!")

    def auto_add_members(self):
        member_names = ["Alice Johnson", "Bob Davis", "Cathy White", "Daniel Black", "Eva Brown"]
        for name in member_names:
            self.member_name_entry.delete(0, tk.END)
            self.member_name_entry.insert(0, name)
            self.member_birthday_entry.set_date(datetime.today())
            self.member_height_entry.delete(0, tk.END)
            self.member_height_entry.insert(0, random.randint(150, 190))
            self.member_weight_entry.delete(0, tk.END)
            self.member_weight_entry.insert(0, random.uniform(50, 100))
            self.activity_level_entry.delete(0, tk.END)
            self.activity_level_entry.insert(0, random.randint(1, 10))

            # Randomly assign a trainer
            assigned_trainer_id = random.choice([1, 2, 3, None])  # Assuming trainer IDs start from 1
            self.trainer_expertise_member_combo.set(random.choice(self.expertise_types))
            self.member_goal_combo.set(random.choice(self.create_goal_options[self.trainer_expertise_member_combo.get()]))

            self.add_member()  # Add member using the existing add_member method

        messagebox.showinfo("Success", "Auto-added members successfully!")

    def add_trainer(self):
        trainer_name = self.trainer_name_entry.get()
        expertise = self.trainer_expertise_combo.get()
        available_days = [day for day, var in self.days_var.items() if var.get()]

        if trainer_name and expertise and available_days:
            conn = sqlite3.connect('gym_simulation.db')
            c = conn.cursor()
            c.execute("INSERT INTO trainers (name, expertise, available_days) VALUES (?, ?, ?)",
                      (trainer_name, expertise, ','.join(available_days)))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Trainer added successfully!")
            self.trainer_name_entry.delete(0, tk.END)
        else:
            messagebox.showerror("Error", "Please fill all fields.")

    def add_member(self):
        member_name = self.member_name_entry.get()
        birthday = self.member_birthday_entry.get()
        height = self.member_height_entry.get()
        weight = self.member_weight_entry.get()
        activity_level = self.activity_level_entry.get()
        goal = self.member_goal_combo.get()
        trainer_expertise = self.trainer_expertise_member_combo.get()

        if member_name and birthday and height and weight and activity_level and goal:
            conn = sqlite3.connect('gym_simulation.db')
            c = conn.cursor()
            c.execute("INSERT INTO members (name, birthday, height, weight, activity_level, goal, protein_needed, carb_needed, fiber_needed) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                      (member_name, birthday, height, weight, activity_level, goal, 0, 0, 0))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Member added successfully!")
            self.member_name_entry.delete(0, tk.END)
            self.member_birthday_entry.set_date(datetime.today())
            self.member_height_entry.delete(0, tk.END)
            self.member_weight_entry.delete(0, tk.END)
            self.activity_level_entry.delete(0, tk.END)
        else:
            messagebox.showerror("Error", "Please fill all fields.")

    def assign_unassigned_members(self):
        conn = sqlite3.connect('gym_simulation.db')
        c = conn.cursor()
        c.execute("SELECT member_id, name FROM members WHERE trainer_id IS NULL")
        unassigned_members = c.fetchall()

        if not unassigned_members:
            messagebox.showinfo("Info", "No unassigned members.")
            return

        c.execute("SELECT trainer_id, name FROM trainers")
        trainers = c.fetchall()

        for member in unassigned_members:
            member_id, member_name = member
            assigned_trainer = random.choice(trainers)
            trainer_id = assigned_trainer[0]
            c.execute("UPDATE members SET trainer_id = ? WHERE member_id = ?", (trainer_id, member_id))
            messagebox.showinfo("Assigned", f"{member_name} has been assigned to trainer {assigned_trainer[1]}.")

        conn.commit()
        conn.close()

    def simulate_progress(self):
        days_passed = self.days_passed_entry.get()
        if not days_passed.isdigit() or int(days_passed) < 0:
            messagebox.showerror("Error", "Please enter a valid number of days.")
            return

        # Simulate progress for each member based on the logic required
        conn = sqlite3.connect('gym_simulation.db')
        c = conn.cursor()
        c.execute("SELECT member_id, weight FROM members")
        members = c.fetchall()

        for member in members:
            member_id = member[0]
            current_weight = member[1]
            # Simulate weight change logic (replace with your own logic)
            new_weight = current_weight - (int(days_passed) * 0.1)  # Example: lose 0.1kg per day
            c.execute("INSERT INTO progress (member_id, date, weight) VALUES (?, ?, ?)",
                      (member_id, datetime.now().strftime("%Y-%m-%d"), new_weight))
            c.execute("UPDATE members SET weight = ? WHERE member_id = ?", (new_weight, member_id))

        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Progress simulated successfully!")

    def view_progress(self):
        member_id = self.member_id_entry.get()
        if not member_id.isdigit():
            messagebox.showerror("Error", "Please enter a valid member ID.")
            return

        conn = sqlite3.connect('gym_simulation.db')
        c = conn.cursor()
        c.execute("SELECT date, weight FROM progress WHERE member_id = ?", (member_id,))
        progress = c.fetchall()
        conn.close()

        if not progress:
            messagebox.showinfo("Progress", "No progress found for this member.")
            return

        progress_list = '\n'.join([f"Date: {entry[0]}, Weight: {entry[1]}" for entry in progress])
        messagebox.showinfo(f"Progress for Member ID {member_id}", progress_list)

if __name__ == "__main__":
    root = tk.Tk()
    app = GymManagementGUI(root)
    root.mainloop()
