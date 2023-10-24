import tkinter as tk
from tkinter import messagebox
from minimain import attendance
from minisho import DbShow
from minipickle import Pickle

class AttendanceApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Attendance System")

        self.pickle_button = tk.Button(self, text="Capture Student Images", command=self.capture_images)
        self.pickle_button.pack(pady=20)

        self.attendance_button = tk.Button(self, text="Mark Attendance", command=self.mark_attendance)
        self.attendance_button.pack(pady=20)

        self.show_db_button = tk.Button(self, text="View Database", command=self.view_database)
        self.show_db_button.pack(pady=20)

    def capture_images(self):
        Pickle.imagesample()

    def mark_attendance(self):
        messagebox.showinfo("Attendance System", "Attendance started. Press 'q' to stop.")
        attendance.first()
        

    def view_database(self):
        DbShow.view_db()

if __name__ == "__main__":
    app = AttendanceApp()
    app.mainloop()
