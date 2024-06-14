import mysql.connector
import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as messagebox
import room 
import subject

def on_next_button_click(root, teacher_id_entry, teacher_name_entry):
    root.destroy()
    open_room_management_window()

def on_prev_button_click(root, teacher_id_entry, teacher_name_entry):
    root.destroy()
    open_subject_window()

def open_room_management_window():
    root = tk.Tk()
    app = room.RoomManagementApp(root)
    root.mainloop()

def open_subject_window():
    root = tk.Tk()
    app = subject.SubjectWindow(root)
    root.mainloop()

class TeacherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Teacher Management System")

        # MySQL connection setup
        self.mydb = mysql.connector.connect(
            host="localhost",
            user="sqluser",
            password="password",
            database="exam"
        )
        self.mycursor = self.mydb.cursor()

        self.setup_ui()

    def setup_ui(self):
        teacher_id_frame = tk.Frame(self.root, padx=10, pady=10)
        teacher_id_frame.grid(row=0, column=0, sticky="w")

        teacher_id_label = tk.Label(teacher_id_frame, text="Teacher ID")
        teacher_id_label.grid(row=0, column=0, padx=5, pady=5)
        self.teacher_id_entry = tk.Entry(teacher_id_frame, width=20)
        self.teacher_id_entry.grid(row=0, column=1, padx=5, pady=5)

        teacher_name_frame = tk.Frame(self.root, padx=10, pady=10)
        teacher_name_frame.grid(row=1, column=0, sticky="w")

        teacher_name_label = tk.Label(teacher_name_frame, text="Teacher Name")
        teacher_name_label.grid(row=0, column=0, padx=5, pady=5)
        self.teacher_name_entry = tk.Entry(teacher_name_frame, width=20)
        self.teacher_name_entry.grid(row=0, column=1, padx=5, pady=5)

        button_frame = tk.Frame(self.root, padx=10, pady=10)
        button_frame.grid(row=2, column=0, sticky="w")

        self.add_button = tk.Button(button_frame, text="Add", command=self.add_record, bg="green", fg="white")
        self.add_button.grid(row=0, column=0, padx=5, pady=5)

        self.update_button = tk.Button(button_frame, text="Update", command=self.update_record, bg="orange", fg="white")
        self.update_button.grid(row=0, column=1, padx=5, pady=5)

        self.delete_button = tk.Button(button_frame, text="Delete", command=self.delete_record, bg="red", fg="white")
        self.delete_button.grid(row=0, column=2, padx=5, pady=5)

        table_frame = tk.Frame(self.root, padx=10, pady=10)
        table_frame.grid(row=3, column=0, sticky="nsew")

        columns = ('#1', '#2')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings')
        self.tree.heading('#1', text='Teacher ID')
        self.tree.heading('#2', text='Teacher Name')
        self.tree.pack(fill=tk.BOTH, expand=True)

        navigation_frame = tk.Frame(self.root, padx=10, pady=10)
        navigation_frame.grid(row=4, column=0, sticky="ew")

        prev_button = tk.Button(navigation_frame, text="Previous", command=lambda: on_prev_button_click(self.root, self.teacher_id_entry, self.teacher_name_entry))
        prev_button.pack(side=tk.LEFT, padx=5, pady=5)

        next_button = tk.Button(navigation_frame, text="Next", command=lambda: on_next_button_click(self.root, self.teacher_id_entry, self.teacher_name_entry))
        next_button.pack(side=tk.RIGHT, padx=5, pady=5)

        # Load data from database
        self.load_data()

    def add_record(self):
        teacher_id = self.teacher_id_entry.get()
        teacher_name = self.teacher_name_entry.get()
        if teacher_id and teacher_name:
            # Insert record into database
            sql = "INSERT INTO teachers (teacher_id, teacher_name) VALUES (%s, %s)"
            val = (teacher_id, teacher_name)
            self.mycursor.execute(sql, val)
            self.mydb.commit()
            # Refresh table
            self.load_data()
            self.teacher_id_entry.delete(0, tk.END)
            self.teacher_name_entry.delete(0, tk.END)
        else:
            messagebox.showerror("Error", "Please enter both Teacher ID and Name")

    def update_record(self):
        selected_item = self.tree.selection()
        if selected_item:
            teacher_id = self.teacher_id_entry.get()
            teacher_name = self.teacher_name_entry.get()
            if teacher_id and teacher_name:
                # Update record in database
                sql = "UPDATE teachers SET teacher_id = %s, teacher_name = %s WHERE teacher_id = %s"
                val = (teacher_id, teacher_name, self.tree.item(selected_item, 'values')[0])
                self.mycursor.execute(sql, val)
                self.mydb.commit()
                # Refresh table
                self.load_data()
            else:
                messagebox.showerror("Error", "Please enter both Teacher ID and Name")
        else:
            messagebox.showerror("Error", "Please select an item to update")

    def delete_record(self):
        selected_item = self.tree.selection()
        if selected_item:
            # Delete record from database
            teacher_id = self.tree.item(selected_item, 'values')[0]
            sql = "DELETE FROM teachers WHERE teacher_id = %s"
            val = (teacher_id,)
            self.mycursor.execute(sql, val)
            self.mydb.commit()
            # Refresh table
            self.load_data()
        else:
            messagebox.showerror("Error", "Please select an item to delete")

    def load_data(self):
        # Clear existing data
        for row in self.tree.get_children():
            self.tree.delete(row)
        # Retrieve data from database
        self.mycursor.execute("SELECT * FROM teachers")
        rows = self.mycursor.fetchall()
        # Insert data into table
        for row in rows:
            self.tree.insert('', 'end', values=row)

if __name__ == "__main__":
    root = tk.Tk()
    app = TeacherApp(root)
    root.mainloop()
