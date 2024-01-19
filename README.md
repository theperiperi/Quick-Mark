# QuickMark: Attendance System with Dual Authentication

## Introduction

QuickMark is an attendance system designed to streamline the attendance tracking process using dual authentication methods: face recognition and QR codes. The system utilizes Tkinter for the frontend user interface and integrates with a database for efficient attendance maintenance.

## Features

- **Dual Authentication:**
  - Face Recognition: Utilizes facial recognition technology to verify and record attendance.
  - QR Codes: Generates and scans QR codes for an additional layer of authentication.

- **User-Friendly Interface:**
  - Built with Tkinter to provide a simple and intuitive frontend for users.

- **Database Integration:**
  - Stores attendance data in a database for easy maintenance and retrieval.

## Requirements

Ensure you have the following dependencies installed:

- Python 3.x
- Tkinter
- OpenCV 
- pyzbar
- pickle

## Usage

1. Launch the application using `python main.py`.
2. Navigate through the intuitive user interface.
3. Authenticate attendees using face recognition or QR code scanning.
4. Attendance data is automatically stored in the database.

## Database Schema

The database contains a table named `attendance` with the following structure:

```sql
CREATE TABLE attendance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id VARCHAR(20) NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Contributions

Contributions are welcome! If you find any issues or want to enhance the functionality, please feel free to create a pull request.

## License

This project is licensed under the MIT License

---

Enjoy using QuickMark! If you have any questions or feedback, feel free to contact me!
