from datetime import datetime, timedelta
import mysql.connector
import tkinter as tk
from tkinter import ttk, messagebox
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
import os
import holidays

class IndiaHolidays:
    def __init__(self):
        self.holiday_cal = holidays.CountryHoliday('IN')

    def is_holiday(self, date):
        return date in self.holiday_cal

class GenerateTimetable:
    def __init__(self, root):
        self.root = root
        self.examination_name = ""  # Placeholder for the examination name
        self.connect_db()
        self.setup_gui()
        self.india_holidays = IndiaHolidays()

    def connect_db(self):
        try:
            self.conn = mysql.connector.connect(
                host="localhost",
                user="sqluser",
                password="password",
                database="exam"
            )
            self.cursor = self.conn.cursor()

            # Fetch start date and end date from the database
            self.cursor.execute("SELECT start_date, end_date FROM date_range")
            self.start_date, self.end_date = self.cursor.fetchone()

            # Fetch data from the database
            self.cursor.execute("SELECT subject_id FROM subjects WHERE backlog = 'Yes'")
            self.backlog_subjects = [row[0] for row in self.cursor.fetchall()]

            self.cursor.execute("SELECT subject_id FROM subjects WHERE backlog = 'No'")
            self.remaining_subjects = [row[0] for row in self.cursor.fetchall()]

            self.cursor.execute("SELECT teacher_name FROM teachers")
            self.teachers = [row[0] for row in self.cursor.fetchall()]

            self.cursor.execute("SELECT room_no FROM rooms")
            self.classrooms = [row[0] for row in self.cursor.fetchall()]

            self.cursor.execute("SELECT slot, slot_time, COALESCE(gap, 0) FROM slot")  # Use COALESCE to handle None values
            self.exam_slots = [(row[0], row[1], row[2]) for row in self.cursor.fetchall()]

            self.all_dates = self.generate_dates(self.start_date, self.end_date)
            self.num_days = len(self.all_dates)
            self.num_backlog_subjects = len(self.backlog_subjects)
            self.num_remaining_subjects = len(self.remaining_subjects)

            if self.num_days < self.num_backlog_subjects + self.num_remaining_subjects:
                raise ValueError("Number of days is less than the number of subjects. Cannot schedule all subjects.")

            # Combine backlog and remaining subjects for scheduling
            self.subjects = self.backlog_subjects + self.remaining_subjects

        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error: {err}")

    def generate_dates(self, start_date, end_date):
        dates = []
        current_date = start_date
        while current_date <= end_date:
            if current_date.weekday() != 6:  # Exclude Sundays
                dates.append(current_date)
            current_date += timedelta(days=1)
        return dates

    def generate_timetable(self):
        timetable = {}
        remaining_subjects = self.subjects.copy()
        teacher_index = 0
        classroom_index = 0
        used_dates = set()

        for date in self.all_dates:
            if self.india_holidays.is_holiday(date):
                continue  # Skip holidays

            if date in used_dates:
                continue  # Skip dates already used

            timetable[date] = {}
            for slot, slot_time, gap in self.exam_slots:
                if remaining_subjects:
                    subject = remaining_subjects.pop(0)
                    teacher = self.teachers[teacher_index % len(self.teachers)]
                    classroom = self.classrooms[classroom_index % len(self.classrooms)]
                    teacher_index += 1
                    classroom_index += 1

                    timetable[date][slot] = {
                        "subject": subject,
                        "teacher": teacher,
                        "classroom": classroom,
                        "slot_time": slot_time
                    }
                    
                    if gap > 0:
                        # Skip the next `gap` number of days
                        for g in range(1, gap + 1):
                            if (date + timedelta(days=g)) in self.all_dates:
                                used_dates.add(date + timedelta(days=g))
                else:
                    timetable[date][slot] = None

        # Ensure any remaining subjects are scheduled
        while remaining_subjects:
            for date in self.all_dates:
                if remaining_subjects:
                    if date not in timetable:
                        timetable[date] = {}

                    for slot, slot_time, gap in self.exam_slots:
                        if remaining_subjects:
                            if slot not in timetable[date]:
                                subject = remaining_subjects.pop(0)
                                teacher = self.teachers[teacher_index % len(self.teachers)]
                                classroom = self.classrooms[classroom_index % len(self.classrooms)]
                                teacher_index += 1
                                classroom_index += 1

                                timetable[date][slot] = {
                                    "subject": subject,
                                    "teacher": teacher,
                                    "classroom": classroom,
                                    "slot_time": slot_time
                                }

                                if gap > 0:
                                    for g in range(1, gap + 1):
                                        if (date + timedelta(days=g)) in self.all_dates:
                                            used_dates.add(date + timedelta(days=g))

        return timetable

    def generate_pdf(self):
        home = os.path.expanduser("~")
        downloads_folder = os.path.join(home, "Downloads")
        pdf_filename = os.path.join(downloads_folder, "exam_timetable.pdf")

        c = canvas.Canvas(pdf_filename, pagesize=A4)
        width, height = A4

        # Add the headings
        heading1 = "Savitribai Phule Pune University"
        heading2 = "Department of Computer Science"
        
        c.setFont("Helvetica-Bold", 8)
        c.drawCentredString(width / 2.0, height - 40, heading1)
        
        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(width / 2.0, height - 60, heading2)

        # Add the examination name
        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(width / 2.0, height - 80, self.examination_name)
        
        c.setFont("Helvetica", 12)
        headers = ["Date", "Day", "Slot", "Slot Time", "Subject", "Teacher", "Classroom"]
        col_widths = [70, 70, 50, 70, 100, 90, 90]  # Increased widths for the first four columns
        row_height = 20
        x_offset = (width - sum(col_widths)) / 2  # Center the table on the page
        y_offset = height - 120

        def draw_grid(x_offset, y_offset, row_height, col_widths, rows):
            c.setStrokeColor(colors.black)
            c.setLineWidth(0.5)
            # Draw horizontal lines
            for i in range(rows + 1):
                y = y_offset - i * row_height
                c.line(x_offset, y, x_offset + sum(col_widths), y)
            # Draw vertical lines
            for i in range(len(col_widths) + 1):
                x = x_offset + sum(col_widths[:i])
                c.line(x, y_offset, x, y_offset - rows * row_height)

        rows = 1  # Start with 1 row for headers
        data = []

        # Prepare data for the table
        for date, slots in self.best_timetable.items():
            day_of_week = date.strftime("%A")
            for slot, exam in slots.items():
                if exam is not None:
                    row_data = [date.strftime("%Y-%m-%d"), day_of_week, slot, exam['slot_time'], exam['subject'], exam['teacher'], exam['classroom']]
                    data.append(row_data)
                    rows += 1

        # Draw the grid for headers
        draw_grid(x_offset, y_offset, row_height, col_widths, rows)

        # Center align column headers and draw grid lines
        for col_num, header in enumerate(headers):
            c.drawCentredString(x_offset + sum(col_widths[:col_num]) + col_widths[col_num] / 2, y_offset - row_height / 2, header)
        y_offset -= row_height

        for row_data in data:
            for col_num, cell in enumerate(row_data):
                c.drawCentredString(x_offset + sum(col_widths[:col_num]) + col_widths[col_num] / 2, y_offset - row_height / 2, str(cell))
            y_offset -= row_height

            if y_offset < 50:
                c.showPage()
                y_offset = height - 50
                # Draw the grid for headers
                draw_grid(x_offset, y_offset, row_height, col_widths, 1)
                # Center align column headers
                for col_num, header in enumerate(headers):
                    c.drawCentredString(x_offset + sum(col_widths[:col_num]) + col_widths[col_num] / 2, y_offset - row_height / 2, header)
                y_offset -= row_height

        c.save()
        messagebox.showinfo("Success", f"PDF has been generated successfully and saved to {pdf_filename}.")

    def setup_gui(self):
        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Arial", 10, "bold"))
        style.configure("Treeview", rowheight=25, font=("Arial", 10))
        style.map("Treeview", background=[("selected", "blue")], foreground=[("selected", "white")])
        
        # Set the Treeview to display grid lines
        style.layout("Treeview", [("Treeview.treearea", {'sticky': 'nswe'})])

        self.tree = ttk.Treeview(self.root, style="Treeview")
        self.tree["columns"] = ("Date", "Day", "Slot", "Slot Time", "Subject", "Teacher", "Classroom")
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)

        self.tree.pack(fill=tk.BOTH, expand=True)

        generate_button = ttk.Button(self.root, text="Generate Timetable", command=self.generate_and_display_timetable)
        generate_button.pack(pady=10)

        pdf_button = ttk.Button(self.root, text="Generate PDF", command=self.prompt_for_exam_name)
        pdf_button.pack(pady=10)

    def generate_and_display_timetable(self):
        self.best_timetable = self.generate_timetable()
        self.display_timetable(self.best_timetable)

    def display_timetable(self, timetable):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for date, slots in timetable.items():
            day_of_week = date.strftime("%A")
            for slot, exam in slots.items():
                if exam is not None:
                    self.tree.insert("", "end", values=(date.strftime("%Y-%m-%d"), day_of_week, slot, exam['slot_time'], exam['subject'], exam['teacher'], exam['classroom']))

    def prompt_for_exam_name(self):
        self.exam_name_window = tk.Toplevel(self.root)
        self.exam_name_window.title("Enter Examination Name")
        
        # Set the size and center the window
        window_width = 600
        window_height = 600
        screen_width = self.exam_name_window.winfo_screenwidth()
        screen_height = self.exam_name_window.winfo_screenheight()
        position_top = int(screen_height / 2 - window_height / 2)
        position_right = int(screen_width / 2 - window_width / 2)
        self.exam_name_window.geometry(f"{window_width}x{window_height}+{position_right}+{position_top}")

        tk.Label(self.exam_name_window, text="Examination Name:").pack(pady=10)
        self.exam_name_entry = tk.Entry(self.exam_name_window, font=("Arial", 14))
        self.exam_name_entry.pack(pady=10)

        submit_button = tk.Button(self.exam_name_window, text="Submit", command=self.set_exam_name)
        submit_button.pack(pady=10)

    def set_exam_name(self):
        self.examination_name = self.exam_name_entry.get()
        self.exam_name_window.destroy()
        self.generate_pdf()

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Exam Timetable")
    app = GenerateTimetable(root)
    root.mainloop()
