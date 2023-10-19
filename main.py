import cv2
import qrcode
from pyzbar.pyzbar import decode
import face_recognition
import pickle
import os

# Load face recognition data from the file
with open('face_data.pkl', 'rb') as f:
    face_data = pickle.load(f)

# Create a directory to store generated QR codes if it doesn't exist
qr_codes_directory = os.path.join(os.path.expanduser("~"), "Desktop", "qr_codes")
if not os.path.exists(qr_codes_directory):
    os.makedirs(qr_codes_directory)

# Generate QR code for attendees and save attendee data
def generate_qr_code(name, file_path):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(name)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(file_path)

# Function to capture video from webcam, decode QR codes, perform face recognition, and mark attendance
def mark_attendance():
    cap = cv2.VideoCapture(0)
    already_marked = set()  # To prevent duplicate entries

    while True:
        _, frame = cap.read()
        decoded_objects = decode(frame)
        
        for obj in decoded_objects:
            qr_data = obj.data.decode('utf-8')
            if qr_data not in already_marked and qr_data in face_data:
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
                        # Here you can insert the attendance record into the database if needed.
        
                    # Draw a rectangle and label around the face
                    cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
                    font = cv2.FONT_HERSHEY_DUPLEX
                    cv2.putText(frame, name, (left + 6, bottom - 6), font, 0.5, (255, 255, 255), 1)

        cv2.imshow("Attendance System", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):  # Press 'q' to exit
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    # Example: Generate QR codes for attendees and save attendee data
    attendees = ["John Doe", "Jane Smith", "Alice Johnson"]

    for attendee in attendees:
        qr_code_path = os.path.join(qr_codes_directory, f"{attendee.replace(' ', '_')}.png")
        generate_qr_code(attendee, qr_code_path)

    # Start attendance marking with face recognition and QR code scanning
    mark_attendance()
