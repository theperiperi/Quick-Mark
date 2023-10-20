#it is sufficient to run line 2 and 3 only once 
from pickling_images import pickle
pickle.imagesample()

from main import attendance
attendance.mark_attendance()
from showattendancedb import db_show
db_show.view_db()