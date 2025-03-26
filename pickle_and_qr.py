import face_recognition
import pickle
import os
import qrcode

class PickleQR:

    @staticmethod
    def imagesload_qrgen():
        # Create directories if they don't exist
        qr_directory = "qr"
        pickle_directory = "pickle_files"
        
        if not os.path.exists(qr_directory):
            os.makedirs(qr_directory)
        if not os.path.exists(pickle_directory):
            os.makedirs(pickle_directory)

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

        face_data = {}
        t = int(input("Enter the number of students to put into the image reference database file: "))
        for i in range(t):
            stu_name = input(f"Enter the name of student {i+1} whose image must be imported: ")
            image_path = os.path.join("classroom", f"{stu_name}.jpg")

            # Check if image exists
            if not os.path.exists(image_path):
                print(f"Error: Image {image_path} not found!")
                continue

            qr_code_path = os.path.join(qr_directory, f"{stu_name.replace(' ', '_')}.png")
            generate_qr_code(stu_name, qr_code_path)

            try:
                s_image = face_recognition.load_image_file(image_path)
                face_encoding = face_recognition.face_encodings(s_image)[0]
                face_data[stu_name] = face_encoding
                print(f"{stu_name} added to image pickle file and QR code generated")
                print(' ')
            except Exception as e:
                print(f"Error processing image for {stu_name}: {str(e)}")
                continue

        # Save the face data to a file using pickle
        pickle_path = os.path.join(pickle_directory, 'face_data.pkl')
        with open(pickle_path, 'wb') as f:
            pickle.dump(face_data, f)
        print("Images have been dumped in the pickle file")
        print('')

# Run the process when the script is executed
if __name__ == "__main__":
    PickleQR.imagesload_qrgen()        