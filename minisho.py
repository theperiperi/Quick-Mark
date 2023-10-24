class DbShow:
    @staticmethod
    def view_db():
        import sqlite3
        # Connect to the SQLite database (attendance.db file in the same directory)
        connection = sqlite3.connect('attendance.db')

        # Create a cursor object to execute SQL queries
        cursor = connection.cursor()

        # Execute a SELECT query to fetch all records from the 'attendance' table
        cursor.execute('SELECT * FROM attendance')

        # Fetch all rows from the cursor
        rows = cursor.fetchall()

        # Print the column headers
        columns = [description[0] for description in cursor.description]
        print('\t'.join(columns))

        # Print the data rows
        for row in rows:
            print('\t'.join(str(cell) for cell in row))

        # Close the cursor and connection
        cursor.close()
        connection.close()
