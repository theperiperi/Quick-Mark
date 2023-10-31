import face_recognition
import pickle
import os
import qrcode

class PickleQR:

    def imagesload_qrgen():

        qr_codes_directory = os.path.join(os.path.expanduser("~"), "Desktop", "qr_codes")
        if not os.path.exists(qr_codes_directory):
            os.makedirs(qr_codes_directory)


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
            imag_path = "C:\\Users\\pri\\Desktop\\classroom\\"+ stu_name + ".jpg"

            qr_code_path = os.path.join(qr_codes_directory, f"{stu_name.replace(' ', '_')}.png")
            generate_qr_code(stu_name, qr_code_path)

            s_image = face_recognition.load_image_file(imag_path)
            face_encoding = face_recognition.face_encodings(s_image)[0]

            # Create a dictionary with face encodings
            face_data[stu_name] = face_encoding

            print(f"{stu_name} added to image pickle file and qr code generated")
            print(' ')

        # Save the face data to a file using pickle
        with open('face_data.pkl', 'wb') as f:
            pickle.dump(face_data, f)
        print("Images have been dumped in the pickle file")
        print('')






            