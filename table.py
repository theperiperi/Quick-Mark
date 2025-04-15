from supabase import create_client, Client
from dotenv import load_dotenv
from tabulate import tabulate
import os

# Load environment variables
load_dotenv()

# Initialize Supabase client
supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

class AttendanceViewer:
    @staticmethod
    def view_attendance(session_id=None):
        """Display attendance records from Supabase."""
        try:
            # Step 1: Fetch attendance records with related student and session data
            query = supabase.table('attendance').select(
                'id, student_id, session_id, timestamp, confidence_score, students(name), sessions(name)'
            )
            if session_id:
                query = query.eq('session_id', session_id)
            records = query.order('timestamp', desc=True).execute()

            # Step 2: Check if records exist
            if not records.data:
                print("No attendance records found")
                return

            # Step 3: Process the records for display
            table_data = []
            for row in records.data:
                student_name = row['students']['name'] if row['students'] else "Unknown"
                session_name = row['sessions']['name'] if row['sessions'] else "Unknown"
                table_data.append([
                    student_name,
                    session_name,
                    row['timestamp'],
                    f"{row['confidence_score']:.2f}"
                ])

            # Step 4: Display the table
            headers = ["Student", "Session", "Timestamp", "Confidence"]
            print(tabulate(table_data, headers=headers, tablefmt="grid"))
        except Exception as e:
            print(f"Error retrieving records: {str(e)}")

if __name__ == "__main__":
    print("Recent Attendance Records:")
    print("------------------------")
    # Example: Filter by session_id if desired
    # session_id = "session_1744686932"
    # AttendanceViewer.view_attendance(session_id)
    AttendanceViewer.view_attendance()