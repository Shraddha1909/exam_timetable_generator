import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as messagebox
import mysql.connector
import teacher
import duration

def on_next_button_click(root):
    root.destroy()
    open_duration_window()

def on_prev_button_click(root):
    root.destroy()
    open_teacher_window()

def open_duration_window():
    root = tk.Tk()
    app = duration.DateRangeApp(root)
    root.mainloop()

def open_teacher_window():
    root = tk.Tk()
    app = teacher.TeacherApp(root)
    root.mainloop()

class RoomManagementApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Room Management")

        # MySQL connection setup
        self.mydb = mysql.connector.connect(
            host="localhost",
            user="sqluser",
            password="password",
            database="exam"
        )
        self.mycursor = self.mydb.cursor()

        self.rooms = []
        self.current_index = 0

        self.main_frame = tk.Frame(master, padx=20, pady=20)
        self.main_frame.grid(row=0, column=0)

        self.room_form_label = tk.Label(self.main_frame, text="Room Form", font=("Arial", 16, "bold"))
        self.room_form_label.grid(row=0, column=0, columnspan=5, pady=(0, 20))

        self.room_label = tk.Label(self.main_frame, text="Room No:")
        self.room_label.grid(row=1, column=0, pady=5)
        self.room_entry = tk.Entry(self.main_frame)
        self.room_entry.grid(row=1, column=1, padx=10, pady=5)

        self.capacity_label = tk.Label(self.main_frame, text="Capacity:")
        self.capacity_label.grid(row=1, column=2, pady=5)
        self.capacity_entry = tk.Entry(self.main_frame)
        self.capacity_entry.grid(row=1, column=3, padx=10, pady=5)

        self.add_button = tk.Button(self.main_frame, text="Add Room", command=self.add_room, bg="#4caf50", fg="white")
        self.add_button.grid(row=2, column=0, padx=10, pady=10)

        self.update_button = tk.Button(self.main_frame, text="Update Room", command=self.update_room, bg="#2196f3", fg="white")
        self.update_button.grid(row=2, column=1, padx=10, pady=10)

        self.delete_button = tk.Button(self.main_frame, text="Delete Room", command=self.delete_room, bg="#f44336", fg="white")
        self.delete_button.grid(row=2, column=2, padx=10, pady=10)

        self.table_frame = tk.Frame(self.main_frame)
        self.table_frame.grid(row=3, columnspan=5, pady=(20, 10))

        self.table = ttk.Treeview(self.table_frame, columns=("Room No", "Capacity"), show="headings", height=10)
        self.table.heading("Room No", text="Room No")
        self.table.heading("Capacity", text="Capacity")
        self.table.grid(row=0, column=0)

        self.button_frame = tk.Frame(self.main_frame)
        self.button_frame.grid(row=4, columnspan=5, pady=(10, 0))

        self.next_button = tk.Button(self.button_frame, text="Next", command=lambda: on_next_button_click(self.master), font=("Arial", 12), bg="#2196f3", fg="white")
        self.next_button.grid(row=0, column=1, padx=10)

        self.prev_button = tk.Button(self.button_frame, text="Previous", command=lambda: on_prev_button_click(self.master), font=("Arial", 12), bg="#2196f3", fg="white")
        self.prev_button.grid(row=0, column=0, padx=10)

        self.update_table()

    def add_room(self):
        room_no = self.room_entry.get()
        capacity = self.capacity_entry.get()
        if room_no and capacity:
            # Insert record into database
            sql = "INSERT INTO rooms (room_no, capacity) VALUES (%s, %s)"
            val = (room_no, capacity)
            self.mycursor.execute(sql, val)
            self.mydb.commit()
            
            self.rooms.append((room_no, capacity))
            self.update_table()
            self.room_entry.delete(0, tk.END)
            self.capacity_entry.delete(0, tk.END)
        else:
            messagebox.showerror("Error", "Please enter both room number and capacity.")

    def update_room(self):
        if self.current_index < len(self.rooms):
            room_no = self.room_entry.get()
            capacity = self.capacity_entry.get()
            if room_no and capacity:
                # Update record in database
                sql = "UPDATE rooms SET room_no = %s, capacity = %s WHERE room_no = %s"
                val = (room_no, capacity, self.rooms[self.current_index][0])
                self.mycursor.execute(sql, val)
                self.mydb.commit()
                
                self.rooms[self.current_index] = (room_no, capacity)
                self.update_table()
            else:
                messagebox.showerror("Error", "Please enter both room number and capacity.")
        else:
            messagebox.showerror("Error", "No room selected.")

    def delete_room(self):
        if self.current_index < len(self.rooms):
            room_no = self.rooms[self.current_index][0]
            # Delete record from database
            sql = "DELETE FROM rooms WHERE room_no = %s"
            val = (room_no,)
            self.mycursor.execute(sql, val)
            self.mydb.commit()
            
            del self.rooms[self.current_index]
            self.update_table()
            if self.current_index >= len(self.rooms):
                self.current_index -= 1
        else:
            messagebox.showerror("Error", "No room selected.")

    def next_room(self):
        if self.current_index < len(self.rooms) - 1:
            self.current_index += 1
            self.update_fields()

    def prev_room(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.update_fields()

    def update_table(self):
        self.table.delete(*self.table.get_children())
        for room in self.rooms:
            self.table.insert("", "end", values=room)

    def update_fields(self):
        if self.current_index < len(self.rooms):
            room_no, capacity = self.rooms[self.current_index]
            self.room_entry.delete(0, tk.END)
            self.room_entry.insert(0, room_no)
            self.capacity_entry.delete(0, tk.END)
            self.capacity_entry.insert(0, capacity)
        else:
            self.room_entry.delete(0, tk.END)
            self.capacity_entry.delete(0, tk.END)

def main():
    root = tk.Tk()
    app = RoomManagementApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
