from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

import pytz

from myapp.booking.room_booking_service import book_room, book_room_fail_version

start = datetime(2022, 4, 7, 2, 30, tzinfo=pytz.utc)
end = datetime(2022, 4, 7, 3, tzinfo=pytz.utc)
book_room('earth', 'tony.stark', start, end)

data = [('room1', 'ted', start, end, 2), ('room1', 'ben', start, end, 0)]


# test with empty table
with ThreadPoolExecutor(2) as e:
	# ted get the room
	for args in data:
		e.submit(book_room, *args)

with ThreadPoolExecutor(2) as e:
	# ben get the room
	for args in data:
		e.submit(book_room_fail_version, *args)
