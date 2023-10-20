class attendance:
    from pyzbar.pyzbar import decode
    import sqlite3

    # Create a connection to the SQLite database (or create a new one if it doesn't exist)
    global conn
    conn = sqlite3.connect('attendance.db')

    global cursor  
    cursor = conn.cursor()

    # Create a table to store attendance data if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    ''')
    conn.commit()

    # Generate QR code for attendees
    def generate_qr_code(data, file_name):
        import qrcode
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        img.save(file_name)

    # Function to capture video from webcam, decode QR codes, and mark attendance in the database
    def mark_attendance():
        from pyzbar.pyzbar import decode
        import cv2
    
        cap = cv2.VideoCapture(0)
        already_marked = set()  # To prevent duplicate entries

        while True:
            _, frame = cap.read()
            decoded_objects =decode(frame)
            
            for obj in decoded_objects:
                qr_data = obj.data.decode('utf-8')
                if qr_data not in already_marked:
                    print(f"Attendance marked for: {qr_data}")
                    cursor.execute('INSERT INTO attendance (name) VALUES (?)', (qr_data,))
                    already_marked.add(qr_data)
                    conn.commit()
            
            cv2.imshow("Attendance System", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):  # Press 'q' to exit
                break

        cap.release()
        cv2.destroyAllWindows()
        conn.close()  # Close the database connection

    if __name__ == "__main__":
        # Example: Generate QR codes for attendees
        attendees = ["John Doe", "Jane Smith", "Alice Johnson"]
        for attendee in attendees:
            generate_qr_code(attendee, f"{attendee.replace(' ', '_')}.png")
        
        
