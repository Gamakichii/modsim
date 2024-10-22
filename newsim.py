import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import sqlite3
import random
from datetime import datetime, timedelta

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
                    available_weeks TEXT)''')

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
                    bmi REAL,
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
        self.available_weeks = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

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

        ttk.Label(self.trainer_frame, text="Available weeks:").grid(row=1, column=0, padx=5, pady=5)
        self.available_weeks_frame = ttk.Frame(self.trainer_frame)
        self.available_weeks_frame.grid(row=1, column=1, columnspan=3)

        self.weeks_var = {day: tk.BooleanVar() for day in self.available_weeks}
        for day, var in self.weeks_var.items():
            ttk.Checkbutton(self.available_weeks_frame, text=day, variable=var).pack(side=tk.LEFT)

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
        ttk.Label(self.progress_frame, text="Weeks Passed:").grid(row=0, column=0, padx=5, pady=5)
        self.weeks_passed_entry = ttk.Entry(self.progress_frame)
        self.weeks_passed_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Button(self.progress_frame, text="Simulate Progress", command=self.simulate_progress).grid(row=0, column=2, padx=5, pady=5)

    def add_view_progress_section(self):
        self.view_progress_member_combo = ttk.Combobox(self.view_progress_frame, state='readonly')
        self.view_progress_member_combo.grid(row=0, column=0, padx=5, pady=5)
        self.view_progress_member_combo.bind("<<ComboboxSelected>>", self.display_member_progress)

        ttk.Button(self.view_progress_frame, text="View Progress", command=self.load_member_progress).grid(row=0, column=1, padx=5, pady=5)

    def update_goals(self, event):
        expertise = self.trainer_expertise_combo.get()
        goals = self.create_goal_options.get(expertise, [])
        self.trainer_expertise_combo['values'] = goals

    def update_goals_member(self, event):
        expertise = self.trainer_expertise_member_combo.get()
        goals = self.create_goal_options.get(expertise, [])
        self.member_goal_combo['values'] = goals

    def add_trainer(self):
        name = self.trainer_name_entry.get()
        expertise = self.trainer_expertise_combo.get()
        available_weeks = ', '.join([day for day, var in self.weeks_var.items() if var.get()])

        if not name or not expertise or not available_weeks:
            messagebox.showerror("Error", "Please fill all fields.")
            return

        conn = sqlite3.connect('gym_simulation.db')
        c = conn.cursor()
        c.execute("INSERT INTO trainers (name, expertise, available_weeks) VALUES (?, ?, ?)",
                  (name, expertise, available_weeks))
        conn.commit()
        conn.close()

        messagebox.showinfo("Success", "Trainer added successfully!")
        self.trainer_name_entry.delete(0, tk.END)
        self.trainer_expertise_combo.set('')
        for var in self.weeks_var.values():
            var.set(False)

    def add_member(self):
        name = self.member_name_entry.get()
        birthday = self.member_birthday_entry.get()
        height = self.member_height_entry.get()
        weight = self.member_weight_entry.get()
        activity_level = self.activity_level_entry.get()
        goal = self.member_goal_combo.get()
        expertise = self.trainer_expertise_member_combo.get()

        if not name or not birthday or not height or not weight or not activity_level or not goal or not expertise:
            messagebox.showerror("Error", "Please fill all fields.")
            return

        try:
            height = int(height)
            weight = float(weight)
            activity_level = int(activity_level)
        except ValueError:
            messagebox.showerror("Error", "Height must be an integer and weight/activity level must be numeric.")
            return

        # Calculate dietary needs
        protein_needed = self.calculate_nutrition(goal, weight, "protein")
        carb_needed = self.calculate_nutrition(goal, weight, "carb")
        fiber_needed = self.calculate_nutrition(goal, weight, "fiber")

        # Retrieve the trainer_id based on the selected expertise
        conn = sqlite3.connect('gym_simulation.db')
        c = conn.cursor()
        c.execute("SELECT trainer_id FROM trainers WHERE expertise = ?", (expertise,))
        trainer = c.fetchone()
        if trainer:
            trainer_id = int(trainer[0])  # Convert trainer_id to integer
        else:
            messagebox.showerror("Error", "No trainer available with the selected expertise.")
            conn.close()
            return

        # Insert member into the database
        c.execute("INSERT INTO members (name, birthday, height, weight, activity_level, goal, protein_needed, carb_needed, fiber_needed, trainer_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                  (name, birthday, height, weight, activity_level, goal, protein_needed, carb_needed, fiber_needed, trainer_id))
        conn.commit()
        conn.close()

        messagebox.showinfo("Success", "Member added successfully!")
        self.member_name_entry.delete(0, tk.END)
        self.member_birthday_entry.delete(0, tk.END)
        self.member_height_entry.delete(0, tk.END)
        self.member_weight_entry.delete(0, tk.END)
        self.activity_level_entry.delete(0, tk.END)
        self.member_goal_combo.set('')
        self.trainer_expertise_member_combo.set('')

    def calculate_nutrition(self, goal, weight, nutrient):
        if nutrient == "protein":
            if goal == "Muscle Gain":
                return 1.5 * weight
            elif goal == "Weight Loss":
                return 1.2 * weight
            else:  # General Health
                return 1.0 * weight
        elif nutrient == "carb":
            if goal == "Muscle Gain":
                return 3.0 * weight
            elif goal == "Weight Loss":
                return 2.5 * weight
            else:  # General Health
                return 2.0 * weight
        elif nutrient == "fiber":
            if goal == "Muscle Gain":
                return 0.03 * weight
            elif goal == "Weight Loss":
                return 0.025 * weight
            else:  # General Health
                return 0.02 * weight

    def view_all_trainers(self):
        conn = sqlite3.connect('gym_simulation.db')
        c = conn.cursor()
        c.execute("SELECT * FROM trainers")
        trainers = c.fetchall()
        conn.close()

        if not trainers:
            messagebox.showinfo("No Trainers", "No trainers found in the database.")
            return

        trainer_list = "\n".join([f"{trainer[0]}: {trainer[1]}, Expertise: {trainer[2]}, Available weeks: {trainer[3]}" for trainer in trainers])
        messagebox.showinfo("Trainers", trainer_list)

    def view_all_members(self):
        conn = sqlite3.connect('gym_simulation.db')
        c = conn.cursor()
        c.execute("SELECT * FROM members")
        members = c.fetchall()
        conn.close()

        if not members:
            messagebox.showinfo("No Members", "No members found in the database.")
            return

        member_list = "\n".join([f"{member[0]}: {member[1]}, Goal: {member[6]}, Trainer ID: {member[10]}" for member in members])
        messagebox.showinfo("Members", member_list)

    def simulate_progress(self):
        try:
            weeks_passed = int(self.weeks_passed_entry.get())
        except ValueError:
            messagebox.showerror("Error", "weeks Passed must be a number.")
            return

        conn = sqlite3.connect('gym_simulation.db')
        c = conn.cursor()
        c.execute("SELECT member_id, name, weight, height, goal, activity_level FROM members")
        members = c.fetchall()

        for member in members:
            member_id, name, initial_weight, height, goal, activity_level = member
            weight_change = 0

            # Adjust weight change based on the member's goal and activity level
            if goal == "Weight Loss":
                weight_change = -initial_weight * (0.01 * weeks_passed * (1 + (activity_level - 5) * 0.1))  # Example: 1% weight loss per week, adjusted by activity level
            elif goal == "Muscle Gain":
                weight_change = initial_weight * (0.005 * weeks_passed * (1 + (activity_level - 5) * 0.1))  # Example: 0.5% weight gain per week, adjusted by activity level
            elif goal == "Fat Loss":
                weight_change = -initial_weight * (0.007 * weeks_passed * (1 + (activity_level - 5) * 0.1))  # Example: 0.7% fat loss per week, adjusted by activity level
            elif goal == "Endurance":
                weight_change = initial_weight * (0.002 * weeks_passed * (1 + (activity_level - 5) * 0.1))  # Example: 0.2% weight gain per week, adjusted by activity level
            elif goal == "Strength":
                weight_change = initial_weight * (0.004 * weeks_passed * (1 + (activity_level - 5) * 0.1))  # Example: 0.4% weight gain per week, adjusted by activity level
            elif goal == "Powerlifting":
                weight_change = initial_weight * (0.003 * weeks_passed * (1 + (activity_level - 5) * 0.1))  # Example: 0.3% weight gain per week, adjusted by activity level
            elif goal == "Core Strength":
                weight_change = initial_weight * (0.002 * weeks_passed * (1 + (activity_level - 5) * 0.1))  # Example: 0.2% weight gain per week, adjusted by activity level
            elif goal == "Flexibility":
                weight_change = initial_weight * (0.001 * weeks_passed * (1 + (activity_level - 5) * 0.1))  # Example: 0.1% weight gain per week, adjusted by activity level
            elif goal == "Rehabilitation":
                weight_change = initial_weight * (0.001 * weeks_passed * (1 + (activity_level - 5) * 0.1))  # Example: 0.1% weight gain per week, adjusted by activity level
            else:  # General Health
                weight_change = initial_weight * (0.002 * weeks_passed * (1 + (activity_level - 5) * 0.1))  # Example: 0.2% weight gain per week, adjusted by activity level

            new_weight = initial_weight + weight_change

            # Get the last recorded progress date for this member
            c.execute("SELECT date FROM progress WHERE member_id = ? ORDER BY date DESC LIMIT 1", (member_id,))
            last_date = c.fetchone()
            if last_date:
                last_date = datetime.strptime(last_date[0], '%Y-%m-%d')
                current_date = last_date + timedelta(weeks=weeks_passed)
            else:
                current_date = datetime.now()

            # Calculate BMI
            bmi = new_weight / ((height / 100) ** 2)

            # Insert progress into the database
            c.execute("INSERT INTO progress (member_id, date, weight, bmi) VALUES (?, ?, ?, ?)",
                    (member_id, current_date.strftime('%Y-%m-%d'), new_weight, bmi))
        conn.commit()
        conn.close()

        messagebox.showinfo("Success", "Progress simulated successfully!")


    def display_member_progress(self, event):
        member_name = self.view_progress_member_combo.get()

        conn = sqlite3.connect('gym_simulation.db')
        c = conn.cursor()
        c.execute("SELECT m.member_id, m.name, m.birthday, m.height, m.weight, m.activity_level, m.goal, m.protein_needed, m.carb_needed, m.fiber_needed, t.name AS trainer_name, t.expertise, p.date, p.weight, p.bmi "
                "FROM members m "
                "LEFT JOIN trainers t ON m.trainer_id = t.trainer_id "
                "LEFT JOIN progress p ON m.member_id = p.member_id "
                "WHERE m.name = ? "
                "ORDER BY p.date ASC", (member_name,))
        member_progress = c.fetchall()
        conn.close()

        if not member_progress:
            messagebox.showinfo("No Progress", f"No progress recorded for {member_name}.")
            return

        progress_list = []
        current_member = None
        for row in member_progress:
            if current_member is None or current_member["name"] != row[1]:
                if current_member:
                    progress_list.append(f"Member: {current_member['name']}")
                    progress_list.append(f"Birthday: {current_member['birthday']}")
                    progress_list.append(f"Height: {current_member['height']} cm")
                    progress_list.append(f"Weight: {current_member['weight']:.2f} kg")
                    progress_list.append(f"Activity Level: {current_member['activity_level']}")
                    progress_list.append(f"Goal: {current_member['goal']}")
                    progress_list.append(f"Protein: {current_member['protein_needed']:.2f} g")
                    progress_list.append(f"Carb: {current_member['carb_needed']:.2f} g")
                    progress_list.append(f"Fiber: {current_member['fiber_needed']:.2f} g")
                    progress_list.append(f"Trainer: {current_member['trainer_name']}")
                    progress_list.append(f"Expertise: {current_member['expertise']}")
                    progress_list.append("")

                current_member = {
                    "name": row[1],
                    "birthday": row[2],
                    "height": row[3],
                    "weight": row[4],
                    "activity_level": row[5],
                    "goal": row[6],
                    "protein_needed": row[7],
                    "carb_needed": row[8],
                    "fiber_needed": row[9],
                    "trainer_name": row[10],
                    "expertise": row[11]
                }

            progress_list.append(f"Date: {row[12]}, Weight: {row[13]:.2f} kg, BMI: {row[14]:.2f}")

        if current_member:
            progress_list.append(f"Member: {current_member['name']}")
            progress_list.append(f"Birthday: {current_member['birthday']}")
            progress_list.append(f"Height: {current_member['height']} cm")
            progress_list.append(f"Weight: {current_member['weight']:.2f} kg")
            progress_list.append(f"Activity Level: {current_member['activity_level']}")
            progress_list.append(f"Goal: {current_member['goal']}")
            progress_list.append(f"Protein: {current_member['protein_needed']:.2f} g")
            progress_list.append(f"Carb: {current_member['carb_needed']:.2f} g")
            progress_list.append(f"Fiber: {current_member['fiber_needed']:.2f} g")
            progress_list.append(f"Trainer: {current_member['trainer_name']}")
            progress_list.append(f"Expertise: {current_member['expertise']}")

        progress_info = "\n".join(progress_list)
        messagebox.showinfo(f"{member_name}'s Progress", progress_info)


    def load_member_progress(self):
        conn = sqlite3.connect('gym_simulation.db')
        c = conn.cursor()
        c.execute("SELECT member_id, name FROM members")
        members = c.fetchall()
        conn.close()

        if not members:
            messagebox.showinfo("No Members", "No members found in the database.")
            return

        self.view_progress_member_combo['values'] = [member[1] for member in members]
        self.view_progress_member_combo.set('')

    def auto_add_trainers(self):
        conn = sqlite3.connect('gym_simulation.db')
        c = conn.cursor()
        for name in self.trainer_names:
            expertise = random.choice(self.expertise_types)
            available_weeks = ', '.join(random.sample(self.available_weeks, 5))  # Randomly select 5 weeks
            c.execute("INSERT INTO trainers (name, expertise, available_weeks) VALUES (?, ?, ?)",
                      (name, expertise, available_weeks))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Auto-added trainers successfully!")

    def auto_add_members(self):
        conn = sqlite3.connect('gym_simulation.db')
        c = conn.cursor()
        for i in range(10):  # Add 10 members
            name = f"Member {i + 1}"
            birthday = "2000-01-01"  # Placeholder date
            height = random.randint(150, 200)
            weight = random.uniform(50.0, 100.0)
            activity_level = random.randint(1, 10)
            goal = random.choice(["Weight Loss", "Muscle Gain", "General Health", "Flexibility Improvement", "Stress Relief", "Mindfulness", "Fat Loss", "Endurance", "Strength", "Strength Building", "Powerlifting", "Core Strength", "Flexibility", "Rehabilitation"])
            expertise = random.choice(self.expertise_types)

            # Calculate protein, carb, and fiber needs
            protein_needed = self.calculate_nutrition(goal, weight, "protein")
            carb_needed = self.calculate_nutrition(goal, weight, "carb")
            fiber_needed = self.calculate_nutrition(goal, weight, "fiber")

            # Retrieve the trainer_id based on the selected expertise
            c.execute("SELECT trainer_id FROM trainers WHERE expertise = ?", (expertise,))
            trainer = c.fetchone()
            if trainer:
                trainer_id = int(trainer[0])  # Convert trainer_id to integer
            else:
                trainer_id = None

            # Insert member into the database
            c.execute("INSERT INTO members (name, birthday, height, weight, activity_level, goal, protein_needed, carb_needed, fiber_needed, trainer_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                      (name, birthday, height, weight, activity_level, goal, protein_needed, carb_needed, fiber_needed, trainer_id))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Auto-added members successfully!")

    def assign_unassigned_members(self):
        conn = sqlite3.connect('gym_simulation.db')
        c = conn.cursor()
        c.execute("SELECT member_id, goal FROM members WHERE trainer_id IS NULL")
        unassigned_members = c.fetchall()

        if not unassigned_members:
            messagebox.showinfo("Info", "No unassigned members to assign.")
            return

        c.execute("SELECT trainer_id, expertise FROM trainers")
        trainers = c.fetchall()

        if not trainers:
            messagebox.showinfo("Info", "No trainers available for assignment.")
            return

        for member_id, member_goal in unassigned_members:
            for trainer_id, expertise in trainers:
                if member_goal in self.create_goal_options[expertise]:
                    c.execute("UPDATE members SET trainer_id = ? WHERE member_id = ?", (trainer_id, member_id))
                    break

        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Unassigned members have been successfully assigned!")
        self.unassigned_assigned = True

# Running the application
if __name__ == "__main__":
    root = tk.Tk()
    app = GymManagementGUI(root)
    root.mainloop()
