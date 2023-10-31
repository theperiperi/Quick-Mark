import tkinter as tk
from tkinter import messagebox
from pickle_and_qr import PickleQR
from table import dbshow
from main import attend

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
        try:
            PickleQR.imagesload_qrgen()
        except Exception as e:
            messagebox.showerror("Error", f"Error occurred: {e}")

    def mark_attendance(self):
        try:
            messagebox.showinfo("Attendance System", "Attendance started. Press 'q' to stop.")
            attend.startprocess()
            messagebox.showinfo("Attendance System", "Attendance marking completed.")
        except Exception as e:
            messagebox.showerror("Error", f"Error occurred: {e}")

    def view_database(self):
        try:
            dbshow.view_db()
        except Exception as e:
            messagebox.showerror("Error", f"Error occurred: {e}")

if __name__ == "__main__":
    app = AttendanceApp()
    app.mainloop()
