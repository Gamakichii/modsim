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
        self.view_member_id_entry = ttk.Entry(self.view_progress_frame)
        self.view_member_id_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Button(self.view_progress_frame, text="View Progress", command=self.view_member_progress).grid(row=1, column=0, columnspan=2, padx=5, pady=5)

    def auto_add_trainers(self):
        for trainer in self.trainer_names:
            self.trainer_name_entry.delete(0, tk.END)
            self.trainer_name_entry.insert(0, trainer)
            self.trainer_expertise_combo.current(random.randint(0, len(self.expertise_types) - 1))
            self.add_trainer()

    def auto_add_members(self):
        for _ in range(5):
            self.member_name_entry.delete(0, tk.END)
            self.member_name_entry.insert(0, f"Member {_ + 1}")
            self.member_birthday_entry.set_date(datetime.today().replace(year=datetime.today().year - random.randint(20, 40)))
            self.member_height_entry.delete(0, tk.END)
            self.member_height_entry.insert(0, random.randint(150, 190))
            self.member_weight_entry.delete(0, tk.END)
            self.member_weight_entry.insert(0, random.randint(50, 100))
            self.activity_level_entry.delete(0, tk.END)
            self.activity_level_entry.insert(0, random.randint(1, 10))
            self.trainer_expertise_member_combo.current(random.randint(0, len(self.expertise_types) - 1))
            self.update_goals_member(None)  # Update goals after setting expertise
            self.member_goal_combo.current(random.randint(0, len(self.create_goal_options[self.expertise_types[self.trainer_expertise_member_combo.current()]]) - 1))
            self.add_member()

    def update_goals(self, event):
        selected_expertise = self.trainer_expertise_combo.get()
        goals = self.create_goal_options.get(selected_expertise, [])
        self.member_goal_combo['values'] = goals
        self.member_goal_combo.set('')  # Clear current selection

    def update_goals_member(self, event):
        selected_expertise = self.trainer_expertise_member_combo.get()
        goals = self.create_goal_options.get(selected_expertise, [])
        self.member_goal_combo['values'] = goals
        self.member_goal_combo.set('')  # Clear current selection

    def assign_unassigned_members(self):
        if not self.unassigned_assigned:
            conn = sqlite3.connect('gym_simulation.db')
            c = conn.cursor()

            # Select all unassigned members
            c.execute("SELECT member_id FROM members WHERE trainer_id IS NULL")
            unassigned_members = c.fetchall()

            # Assign each unassigned member to a random trainer
            for member in unassigned_members:
                trainer_id = random.randint(1, len(self.trainer_names))  # Assuming trainer IDs start from 1
                c.execute("UPDATE members SET trainer_id = ? WHERE member_id = ?", (trainer_id, member[0]))

            conn.commit()
            conn.close()
            self.unassigned_assigned = True
            messagebox.showinfo("Success", "Unassigned members have been assigned to trainers.")
        else:
            messagebox.showwarning("Warning", "Members have already been assigned to trainers.")

    def simulate_progress(self):
        days_passed = int(self.days_passed_entry.get())
        conn = sqlite3.connect('gym_simulation.db')
        c = conn.cursor()

        c.execute("SELECT member_id, weight FROM members")
        members = c.fetchall()

        for member in members:
            weight_change = random.uniform(-1, 1)  # Simulating weight change
            new_weight = member[1] + weight_change
            c.execute("INSERT INTO progress (member_id, date, weight) VALUES (?, ?, ?)", (member[0], datetime.now().date(), new_weight))

        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Progress simulated successfully.")

    def view_member_progress(self):
        member_id = self.view_member_id_entry.get()
        conn = sqlite3.connect('gym_simulation.db')
        c = conn.cursor()

        c.execute("SELECT * FROM progress WHERE member_id = ?", (member_id,))
        progress_data = c.fetchall()

        if progress_data:
            progress_info = "\n".join([f"Date: {data[1]}, Weight: {data[2]}" for data in progress_data])
            messagebox.showinfo("Progress Data", f"Member ID: {member_id}\n{progress_info}")
        else:
            messagebox.showwarning("No Data", "No progress data found for this member.")

        conn.close()

    def add_trainer(self):
        name = self.trainer_name_entry.get()
        expertise = self.trainer_expertise_combo.get()
        available_days = [day for day, var in self.days_var.items() if var.get()]
        available_days_str = ', '.join(available_days)

        conn = sqlite3.connect('gym_simulation.db')
        c = conn.cursor()

        c.execute("INSERT INTO trainers (name, expertise, available_days) VALUES (?, ?, ?)",
                  (name, expertise, available_days_str))
        conn.commit()
        conn.close()

        messagebox.showinfo("Success", f"Trainer '{name}' added successfully.")

    def add_member(self):
        name = self.member_name_entry.get()
        birthday = self.member_birthday_entry.get()
        height = self.member_height_entry.get()
        weight = self.member_weight_entry.get()
        activity_level = self.activity_level_entry.get()
        goal = self.member_goal_combo.get()
        trainer_expertise = self.trainer_expertise_member_combo.get()

        protein_needed = float(weight) * 0.2  # Example calculation
        carb_needed = float(weight) * 0.5  # Example calculation
        fiber_needed = float(weight) * 0.1  # Example calculation

        conn = sqlite3.connect('gym_simulation.db')
        c = conn.cursor()

        c.execute("INSERT INTO members (name, birthday, height, weight, activity_level, goal, protein_needed, carb_needed, fiber_needed) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                  (name, birthday, height, weight, activity_level, goal, protein_needed, carb_needed, fiber_needed))
        conn.commit()
        conn.close()

        messagebox.showinfo("Success", f"Member '{name}' added successfully.")

    def view_all_trainers(self):
        conn = sqlite3.connect('gym_simulation.db')
        c = conn.cursor()

        c.execute("SELECT * FROM trainers")
        trainers = c.fetchall()
        conn.close()

        if trainers:
            trainers_info = "\n".join([f"ID: {trainer[0]}, Name: {trainer[1]}, Expertise: {trainer[2]}, Available Days: {trainer[3]}" for trainer in trainers])
            messagebox.showinfo("All Trainers", trainers_info)
        else:
            messagebox.showinfo("No Trainers", "No trainers found.")

    def view_all_members(self):
        conn = sqlite3.connect('gym_simulation.db')
        c = conn.cursor()

        c.execute("SELECT * FROM members")
        members = c.fetchall()
        conn.close()

        if members:
            members_info = "\n".join([f"ID: {member[0]}, Name: {member[1]}, Height: {member[3]}, Weight: {member[4]}" for member in members])
            messagebox.showinfo("All Members", members_info)
        else:
            messagebox.showinfo("No Members", "No members found.")

# Run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = GymManagementGUI(root)
    root.mainloop()
