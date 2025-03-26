import cv2
import qrcode
from pyzbar.pyzbar import decode
from pyzbar.pyzbar import ZBarSymbol
import face_recognition
import pickle
import sqlite3
import os

class attend:
    def startprocess():
        # Establish a connection to the database (or create a new one if it doesn't exist)
        conn = sqlite3.connect('attendance.db')
        c = conn.cursor()

        # Create a table to store attendance data with the correct schema
        c.execute('''CREATE TABLE IF NOT EXISTS attendance
                    (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')

        # Commit the changes and close the connection
        conn.commit()
        conn.close()

        # Load face recognition data from the file
        pickle_path = os.path.join('pickle_files', 'face_data.pkl')
        if not os.path.exists(pickle_path):
            print(f"Error: Pickle file not found at {pickle_path}")
            return

        with open(pickle_path, 'rb') as f:
            face_data = pickle.load(f)

        # Function to capture video from webcam, decode QR codes, perform face recognition, and mark attendance
        def mark_attendance():
            # Open the database connection outside the loop
            conn = sqlite3.connect('attendance.db')
            c = conn.cursor()

            cap = cv2.VideoCapture(0)
            already_marked = set()  # To prevent duplicate entries

            while True:
                _, frame = cap.read()
                decoded_objects = decode(frame, symbols=[ZBarSymbol.QRCODE])
                
                for obj in decoded_objects:
                    qr_data = obj.data.decode('utf-8') if obj.data else None
                    if qr_data and qr_data not in already_marked and qr_data in face_data:
                        face_locations = face_recognition.face_locations(frame)
                        face_encodings = face_recognition.face_encodings(frame, face_locations)

                        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                            # Compare the face encoding with known face encodings
                            matches = face_recognition.compare_faces([face_data[qr_data]], face_encoding)
                            name = "Unknown"

                            if matches[0]:
                                name = qr_data
                                print(f"Attendance marked for: {name}")
                                already_marked.add(qr_data)

                                # Store attendance data in the database
                                # Check if the attendee is in the face_data dictionary
                                if qr_data in face_data:
                                    status = 'Present'
                                else:
                                    status = 'Absent'

                                # Insert attendance record into the database
                                c.execute("INSERT INTO attendance (name) VALUES (?)", (name,))
                                conn.commit()  # Commit the changes

                            # Draw a rectangle and label around the face
                            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
                            font = cv2.FONT_HERSHEY_DUPLEX
                            cv2.putText(frame, name, (left + 6, bottom - 6), font, 0.5, (255, 255, 255), 1)

                cv2.imshow("Attendance System", frame)

                if cv2.waitKey(1) & 0xFF == ord('q'):  # Press 'q' to exit
                    break

            # Close the connection after the loop ends
            conn.close()

            cap.release()
            cv2.destroyAllWindows()

        # Call the mark_attendance function
        mark_attendance()

# Run the attendance system when the script is executed
if __name__ == "__main__":
    attend.startprocess()
