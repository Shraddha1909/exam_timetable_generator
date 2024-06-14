import mysql.connector
import tkinter as tk
from tkinter import ttk, messagebox
import teacher
import main1

def on_next_button_click(root):
    root.destroy()
    open_teacher_window()

def on_prev_button_click(root):
    root.destroy()
    open_main1_window()

def open_teacher_window(): 
    root = tk.Tk()
    app = teacher.TeacherApp(root)
    root.mainloop()

def open_main1_window():
    root = tk.Tk()
    app = main1.MainpageExam(root)
    root.mainloop()

class SubjectWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Subject Management System")
        self.root.configure(bg='#f0f0f0')

        window_width = 800
        window_height = 800
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x_coordinate = (screen_width / 2) - (window_width / 2)
        y_coordinate = (screen_height / 2) - (window_height / 2)
        root.geometry("%dx%d+%d+%d" % (window_width, window_height, x_coordinate, y_coordinate))

        custom_font = ('Helvetica', 12)

        self.subject_form_label = tk.Label(self.root, text='Subject Form', font=('Helvetica', 16, 'bold'), bg='#f0f0f0')
        self.subject_form_label.pack(pady=10)

        self.subject_id_var = tk.StringVar()
        self.subject_name_var = tk.StringVar()
        self.backlog_var = tk.StringVar()

        self.subject_id_label = tk.Label(self.root, text='Subject ID:', font=custom_font, bg='#f0f0f0', anchor='w')
        self.subject_id_label.pack(pady=5, padx=10, anchor='w', fill='x')
        self.subject_id_entry = tk.Entry(self.root, textvariable=self.subject_id_var, font=custom_font, width=10)
        self.subject_id_entry.pack(pady=5, padx=10, anchor='w', fill='x')

        self.subject_name_label = tk.Label(self.root, text='Subject Name:', font=custom_font, bg='#f0f0f0', anchor='w')
        self.subject_name_label.pack(pady=5, padx=10, anchor='w', fill='x')
        self.subject_name_entry = tk.Entry(self.root, textvariable=self.subject_name_var, font=custom_font, width=10)
        self.subject_name_entry.pack(pady=5, padx=10, anchor='w', fill='x')

        self.backlog_label = tk.Label(self.root, text='Backlog:', font=custom_font, bg='#f0f0f0', anchor='w')
        self.backlog_label.pack(pady=5, padx=10, anchor='w', fill='x')
        self.backlog_frame = tk.Frame(self.root, bg='#f0f0f0')
        self.backlog_frame.pack(pady=5, padx=10, anchor='w', fill='x')
        self.backlog_yes_radio = tk.Radiobutton(self.backlog_frame, text='Yes', variable=self.backlog_var, value='Yes', font=custom_font, bg='#f0f0f0', fg='blue')
        self.backlog_yes_radio.pack(side=tk.LEFT)
        self.backlog_no_radio = tk.Radiobutton(self.backlog_frame, text='No', variable=self.backlog_var, value='No', font=custom_font, bg='#f0f0f0', fg='green')
        self.backlog_no_radio.pack(side=tk.LEFT)

        self.add_button = tk.Button(self.root, text='Add Subject', command=self.add_subject, font=custom_font, bg='green', fg='white')
        self.add_button.pack(pady=10)

        self.update_button = tk.Button(self.root, text='Update Subject', command=self.update_subject, font=custom_font, bg='blue', fg='white')
        self.update_button.pack(pady=10)

        self.delete_button = tk.Button(self.root, text='Delete Subject', command=self.delete_subject, font=custom_font, bg='red', fg='white')
        self.delete_button.pack(pady=10)

        self.subject_table = ttk.Treeview(self.root, columns=('ID', 'Name', 'Backlog'), show='headings', height=10)
        self.subject_table.heading('ID', text='ID')
        self.subject_table.heading('Name', text='Name')
        self.subject_table.heading('Backlog', text='Backlog')
        self.subject_table.pack(pady=10)

        self.next_button = tk.Button(self.root, text='Next', font=custom_font, bg='purple', fg='white', command=lambda: on_next_button_click(root))
        self.next_button.pack(pady=10)

        self.prev_button = tk.Button(self.root, text='Previous', font=custom_font, bg='orange', fg='white', command=lambda: on_prev_button_click(root))
        self.prev_button.pack(pady=10)

        # MySQL connection setup
        self.mydb = mysql.connector.connect(
            host="localhost",
            user="sqluser",
            password="password",
            database="exam"
        )
        self.mycursor = self.mydb.cursor()

        self.load_data()

    def add_subject(self):
        subject_id = self.subject_id_var.get()
        subject_name = self.subject_name_var.get()
        backlog = self.backlog_var.get()

        if not subject_id or not subject_name or not backlog:
            messagebox.showerror("Input Error", "All fields must be filled out")
            return

        # Insert record into database
        sql = "INSERT INTO subjects (subject_id, subject_name, backlog) VALUES (%s, %s, %s)"
        val = (subject_id, subject_name, backlog)
        self.mycursor.execute(sql, val)
        self.mydb.commit()

        # Refresh table
        self.load_data()

    def update_subject(self):
        selected_item = self.subject_table.selection()
        if not selected_item:
            messagebox.showerror("Selection Error", "No subject selected")
            return

        subject_id = self.subject_id_var.get()
        subject_name = self.subject_name_var.get()
        backlog = self.backlog_var.get()

        if not subject_id or not subject_name or not backlog:
            messagebox.showerror("Input Error", "All fields must be filled out")
            return

        # Update record in database
        sql = "UPDATE subjects SET subject_id = %s, subject_name = %s, backlog = %s WHERE subject_id = %s"
        val = (subject_id, subject_name, backlog, self.subject_table.item(selected_item, 'values')[0])
        self.mycursor.execute(sql, val)
        self.mydb.commit()

        # Refresh table
        self.load_data()

    def delete_subject(self):
        selected_item = self.subject_table.selection()
        if not selected_item:
            messagebox.showerror("Selection Error", "No subject selected")
            return

        subject_id = self.subject_table.item(selected_item, 'values')[0]

        # Delete record from database
        sql = "DELETE FROM subjects WHERE subject_id = %s"
        val = (subject_id,)
        self.mycursor.execute(sql, val)
        self.mydb.commit()

        # Refresh table
        self.load_data()

    def load_data(self):
        # Clear existing data
        for row in self.subject_table.get_children():
            self.subject_table.delete(row)

        # Retrieve data from database
        self.mycursor.execute("SELECT * FROM subjects")
        rows = self.mycursor.fetchall()

        # Insert data into table
        for row in rows:
            self.subject_table.insert('', 'end', values=row)

    
if __name__ == "__main__":
    root = tk.Tk()
    app = SubjectWindow(root)
    root.mainloop()
