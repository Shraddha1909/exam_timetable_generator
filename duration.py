import tkinter as tk
from tkinter import ttk
from tkcalendar import Calendar, DateEntry
import tkinter.messagebox as messagebox
import mysql.connector
import room
import slot
import datetime
import holidays  # Import the holidays package

def on_next_button_click(root):
    root.destroy()
    open_slot_window()

def on_prev_button_click(root):
    root.destroy()
    open_room_window()

def open_slot_window():
    root = tk.Tk()
    app = slot.TimetableApp(root)
    root.mainloop()

def open_room_window():
    root = tk.Tk()
    app = room.RoomManagementApp(root)
    root.mainloop()

class HolidayCalendar(Calendar):
    def __init__(self, master=None, **kwargs):
        self.holidays = kwargs.pop('holidays', [])
        Calendar.__init__(self, master, **kwargs)
        self.tag_config('holiday', background='red', foreground='white')
        self._highlight_holidays()

    def _highlight_holidays(self):
        for holiday in self.holidays:
            self.calevent_create(holiday, 'Holiday', 'holiday')

class DateRangeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Date Range Selector")
        
        # MySQL connection setup
        self.mydb = mysql.connector.connect(
            host="localhost",
            user="sqluser",
            password="password",
            database="exam"
        )
        self.mycursor = self.mydb.cursor()

        # Fetch public holidays for India
        self.public_holidays = self.fetch_public_holidays()

        self.setup_ui()

    def fetch_public_holidays(self):
        india_holidays = holidays.India(years=range(2020, 2030))  # Fetch holidays for a range of years
        return [date for date in india_holidays]

    def setup_ui(self):
        # Create a frame for the date selection
        date_frame = tk.Frame(self.root, padx=10, pady=10)
        date_frame.grid(row=0, column=0, sticky="w")

        # Start date label and calendar
        start_label = tk.Label(date_frame, text="Start Date")
        start_label.grid(row=0, column=0, padx=5, pady=5)
        self.start_date = HolidayCalendar(date_frame, selectmode='day', date_pattern='yyyy-mm-dd', holidays=self.public_holidays)
        self.start_date.grid(row=1, column=0, padx=5, pady=5, columnspan=2)

        # End date label and calendar
        end_label = tk.Label(date_frame, text="End Date")
        end_label.grid(row=0, column=2, padx=5, pady=5)
        self.end_date = HolidayCalendar(date_frame, selectmode='day', date_pattern='yyyy-mm-dd', holidays=self.public_holidays)
        self.end_date.grid(row=1, column=2, padx=5, pady=5, columnspan=2)

        # Buttons
        button_frame = tk.Frame(self.root, padx=10, pady=10)
        button_frame.grid(row=2, column=0, sticky="w")

        self.add_button = tk.Button(button_frame, text="Add", command=self.add_record, bg="green", fg="white")
        self.add_button.grid(row=0, column=0, padx=5, pady=5)

        self.update_button = tk.Button(button_frame, text="Update", command=self.update_record, bg="orange", fg="white")
        self.update_button.grid(row=0, column=1, padx=5, pady=5)

        self.delete_button = tk.Button(button_frame, text="Delete", command=self.delete_record, bg="red", fg="white")
        self.delete_button.grid(row=0, column=2, padx=5, pady=5)

        # Table
        table_frame = tk.Frame(self.root, padx=10, pady=10)
        table_frame.grid(row=3, column=0, sticky="nsew")

        columns = ('#1', '#2')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings')
        self.tree.heading('#1', text='Start Date')
        self.tree.heading('#2', text='End Date')

        self.tree.grid(row=0, column=0, sticky='nsew')

        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky='ns')
        
        navigation_frame = tk.Frame(self.root, padx=10, pady=10)
        navigation_frame.grid(row=4, column=0, sticky="ew")
       
        prev_button = tk.Button(navigation_frame, text="Previous", command=lambda: on_prev_button_click(self.root))
        prev_button.pack(side=tk.LEFT, padx=5, pady=5)

        next_button = tk.Button(navigation_frame, text="Next", command=lambda: on_next_button_click(self.root))
        next_button.pack(side=tk.RIGHT, padx=5, pady=5)

    def add_record(self):
        start_date = self.start_date.get_date()
        end_date = self.end_date.get_date()
        if start_date in self.public_holidays or end_date in self.public_holidays:
            messagebox.showwarning("Input Error", "Selected dates include a public holiday.")
            return
        self.tree.insert('', 'end', values=(start_date, end_date))
        # Insert record into database
        sql = "INSERT INTO date_range (start_date, end_date) VALUES (%s, %s)"
        val = (start_date, end_date)
        self.mycursor.execute(sql, val)
        self.mydb.commit()

    def update_record(self):
        selected_item = self.tree.selection()
        if selected_item:
            start_date = self.start_date.get_date()
            end_date = self.end_date.get_date()
            if start_date in self.public_holidays or end_date in self.public_holidays:
                messagebox.showwarning("Input Error", "Selected dates include a public holiday.")
                return
            self.tree.item(selected_item, values=(start_date, end_date))
            # Update record in database
            sql = "UPDATE date_range SET start_date = %s, end_date = %s WHERE start_date = %s AND end_date = %s"
            val = (start_date, end_date, self.tree.item(selected_item, 'values')[0], self.tree.item(selected_item, 'values')[1])
            self.mycursor.execute(sql, val)
            self.mydb.commit()
        else:
            messagebox.showwarning("Update Error", "Please select a record to update")

    def delete_record(self):
        selected_item = self.tree.selection()
        if selected_item:
            self.tree.delete(selected_item)
            # Delete record from database
            sql = "DELETE FROM date_range WHERE start_date = %s AND end_date = %s"
            val = (self.tree.item(selected_item, 'values')[0], self.tree.item(selected_item, 'values')[1])
            self.mycursor.execute(sql, val)
            self.mydb.commit()
        else:
            messagebox.showwarning("Delete Error", "Please select a record to delete")

if __name__ == "__main__":
    root = tk.Tk()
    app = DateRangeApp(root)
    root.mainloop()
