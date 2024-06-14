import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as messagebox
import mysql.connector
import duration
import generate

def on_prev_button_click(root):
    root.destroy()
    open_duration_window()

def open_duration_window():
    root = tk.Tk()
    app = duration.DateRangeApp(root)
    root.mainloop()

def on_generate_button_click(root, slot_var, slot_time_entries, gap_var):
    root.destroy()
    open_generate_window()

def open_generate_window():
    root = tk.Tk()
    app = generate.GenerateTimetable(root)
    root.mainloop()

class TimetableApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Timetable Generator")

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
        # Create a frame for the slot selection
        slot_frame = tk.Frame(self.root, padx=10, pady=10)
        slot_frame.grid(row=0, column=0, sticky="w")

        # Slot label and dropdown
        slot_label = tk.Label(slot_frame, text="Slot")
        slot_label.grid(row=0, column=0, padx=5, pady=5)
        self.slot_var = tk.StringVar()
        self.slot_dropdown = ttk.Combobox(slot_frame, textvariable=self.slot_var, state="readonly")
        self.slot_dropdown['values'] = ('1', '2', '3', '4', '5')
        self.slot_dropdown.grid(row=0, column=1, padx=5, pady=5)
        self.slot_dropdown.bind("<<ComboboxSelected>>", self.update_slot_times)

        # Slot time labels and entries frame
        self.slot_time_frame = tk.Frame(self.root, padx=10, pady=10)
        self.slot_time_frame.grid(row=1, column=0, sticky="w")
        
        self.slot_time_entries = []

        # Gap label and dropdown
        gap_label = tk.Label(slot_frame, text="Gap")
        gap_label.grid(row=1, column=0, padx=5, pady=5)
        self.gap_var = tk.StringVar()
        self.gap_dropdown = ttk.Combobox(slot_frame, textvariable=self.gap_var, state="readonly")
        self.gap_dropdown['values'] = ('0', '1', '2', '3', '4', '5')
        self.gap_dropdown.grid(row=1, column=1, padx=5, pady=5)

        # Buttons
        button_frame = tk.Frame(self.root, padx=10, pady=10)
        button_frame.grid(row=3, column=0, sticky="w")

        self.add_button = tk.Button(button_frame, text="Add", command=self.add_record, bg="green", fg="white")
        self.add_button.grid(row=0, column=0, padx=5, pady=5)

        self.update_button = tk.Button(button_frame, text="Update", command=self.update_record, bg="orange", fg="white")
        self.update_button.grid(row=0, column=1, padx=5, pady=5)

        self.delete_button = tk.Button(button_frame, text="Delete", command=self.delete_record, bg="red", fg="white")
        self.delete_button.grid(row=0, column=2, padx=5, pady=5)
        
        navigation_frame = tk.Frame(self.root, padx=10, pady=10)
        navigation_frame.grid(row=5, column=0, sticky="ew")
       
        generate_button = tk.Button(navigation_frame, text="Generate Timetable", command=lambda: on_generate_button_click(self.root, self.slot_var, self.slot_time_entries, self.gap_var))
        generate_button.pack(side=tk.RIGHT, padx=5, pady=5)
       
        prev_button = tk.Button(navigation_frame, text="Previous", command=lambda: on_prev_button_click(self.root))
        prev_button.pack(side=tk.LEFT, padx=5, pady=5)

        # Table
        table_frame = tk.Frame(self.root, padx=10, pady=10)
        table_frame.grid(row=4, column=0, sticky="nsew")

        columns = ('#1', '#2', '#3')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings')
        self.tree.heading('#1', text='Slot')
        self.tree.heading('#2', text='Slot Time')
        self.tree.heading('#3', text='Gap')

        self.tree.grid(row=0, column=0, sticky='nsew')

        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky='ns')

    def update_slot_times(self, event):
        # Clear existing slot time entries
        for widget in self.slot_time_frame.winfo_children():
            widget.destroy()
        self.slot_time_entries.clear()

        # Get the selected number of slots
        num_slots = int(self.slot_var.get())

        # Create slot time labels and entries dynamically
        for i in range(num_slots):
            slot_time_label = tk.Label(self.slot_time_frame, text=f"Slot Time {i+1}")
            slot_time_label.grid(row=i, column=0, padx=5, pady=5)
            slot_time_entry = ttk.Entry(self.slot_time_frame, width=12)
            slot_time_entry.grid(row=i, column=1, padx=5, pady=5)
            self.slot_time_entries.append(slot_time_entry)

    def add_record(self):
        if len(self.tree.get_children()) >= 1:
            messagebox.showwarning("Add Error", "Only one entry is allowed.")
            return
        slot = self.slot_var.get()
        gap = self.gap_var.get()
        slot_times = [entry.get() for entry in self.slot_time_entries]
        if slot and all(slot_times) and gap:
            for i, slot_time in enumerate(slot_times, 1):
                self.tree.insert('', 'end', values=(f"Slot {i}", slot_time, gap))
                # Insert record into database
                sql = "INSERT INTO slot (slot, slot_time, gap) VALUES (%s, %s, %s)"
                val = (f"Slot {i}", slot_time, gap)
                self.mycursor.execute(sql, val)
                self.mydb.commit()
        else:
            messagebox.showwarning("Input Error", "Please select slot, enter all slot times, and select a gap.")

    def update_record(self):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("Update Error", "Please select a record to update")
            return
        slot_times = [entry.get() for entry in self.slot_time_entries]
        gap = self.gap_var.get()
        if slot_times and all(slot_times) and gap:
            for item, slot_time in zip(selected_items, slot_times):
                self.tree.item(item, values=(self.tree.item(item, 'values')[0], slot_time, gap))
                # Update record in database
                sql = "UPDATE slot SET slot_time = %s, gap = %s WHERE slot = %s"
                val = (slot_time, gap, self.tree.item(item, 'values')[0])
                self.mycursor.execute(sql, val)
                self.mydb.commit()
        else:
            messagebox.showwarning("Input Error", "Please enter all slot times and select a gap.")

    def delete_record(self):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("Delete Error", "Please select a record to delete")
            return
        for selected_item in selected_items:
            self.tree.delete(selected_item)
            # Delete record from database
            sql = "DELETE FROM slot WHERE slot = %s"
            val = (self.tree.item(selected_item, 'values')[0],)
            self.mycursor.execute(sql, val)
            self.mydb.commit()

if __name__ == "__main__":
    root = tk.Tk()
    app = TimetableApp(root)
    root.mainloop()
