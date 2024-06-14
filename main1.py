import tkinter as tk
from tkinter import messagebox
import subject

def onclickbutton():
    exam_name = app.entry.get().strip()
    if not exam_name:
        messagebox.showerror("Error", "Please Enter Examination Name First")
    else:
        root.destroy()
        open_subject_window()

def open_subject_window():
    root = tk.Tk()
    app = subject.SubjectWindow(root)
    root.mainloop()

class MainpageExam:
    def __init__(self, root):
        self.root = root
        self.root.title("Exam Timetable Scheduler")
        self.root.geometry("600x600")

        self.frame = tk.Frame(root)
        self.frame.pack(expand=True)

        self.label = tk.Label(self.frame, text="Enter Examination Name")
        self.label.pack()

        self.entry = tk.Entry(self.frame)
        self.entry.pack()

        self.button = tk.Button(self.frame, text="Submit", command=onclickbutton)
        self.button.pack()

if __name__ == "__main__":
    root = tk.Tk()
    app = MainpageExam(root)
    root.mainloop()