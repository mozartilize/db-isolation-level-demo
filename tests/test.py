from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

import pytz

from myapp.booking.room_booking_service import book_room_serializable, book_room_no_guard, book_room_materializing_conflicts

start1 = datetime(2022, 4, 7, 2, 30, tzinfo=pytz.utc)
end1 = datetime(2022, 4, 7, 3, tzinfo=pytz.utc)

start2 = datetime(2022, 4, 7, 2, 45, tzinfo=pytz.utc)
end2 = datetime(2022, 4, 7, 3, 15, tzinfo=pytz.utc)
data = [('room1', 'ted', start1, end1, 0), ('room1', 'ben', start2, end2, 0)]


# test with empty table
with ThreadPoolExecutor(2) as e:
	# only one of them gets the room
	for args in data:
		e.submit(book_room_materializing_conflicts, *args)

with ThreadPoolExecutor(2) as e:
	# both get the room
	for args in data:
		e.submit(book_room_no_guard, *args)
