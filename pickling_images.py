class pickle:
    def imagesample():
        import face_recognition
        import pickle
        import os
            
        face_data={}
        t=int(input("enter number of students to put into image reference database file"))
        for i in range(t):
            stu_name = input("enter name of student who's image must be imported ")
            imag_path = "C:\\Users\\pri\\Desktop\\" + stu_name + ".jpg"

            s_image=face_recognition.load_image_file(imag_path)
            face_encoding = face_recognition.face_encodings(s_image)[0]
            
            # Create a dictionary with face encodings
            face_data[stu_name]=face_encoding

            print(stu_name," added to image pickle file")
           

        # Save the face data to a file using pickle
        with open('face_data.pkl', 'wb') as f:
            pickle.dump(face_data, f)

   
