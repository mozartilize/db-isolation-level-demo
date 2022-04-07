from datetime import datetime, time
from time import sleep

import pytz
from django.db import OperationalError, transaction, connections
from tenacity import retry, stop_after_attempt, retry_if_exception_type

from .models import RoomBooking


def book_room_materializing_conflicts(room_id, user, start_time, end_time, sleep_sec=0):
	start_time_in_min_time = datetime.combine(start_time.date(), time(0), pytz.utc)
	start_time_in_max_time = datetime.combine(start_time.date(), time(23, 59, 59, 999999), pytz.utc)
	indicator_booking, created = RoomBooking.objects.get_or_create(
		room_id=room_id,
		start_time=start_time_in_min_time,
		end_time=start_time_in_max_time,
		defaults={"user": user}
	)

	with transaction.atomic():
		current_room_bookings = RoomBooking.objects.filter(room_id=room_id).select_for_update()
		# this select will wait util acquire the lock
		current_room_bookings  # type: ignore
		if sleep_sec > 0:
			with connections["default"].cursor() as cur:
				cur.execute(f"select sleep({sleep_sec})")
		check_query = current_room_bookings.filter(start_time__lt=end_time, end_time__gt=start_time)
		if created:
			if check_query.exclude(pk=indicator_booking.pk).exists():
				indicator_booking.delete()
				return None
		else:
			if check_query.exists():
				return None
		if not created:
			indicator_booking = RoomBooking(
				room_id=room_id,
				user=user,
			)
		indicator_booking.start_time = start_time
		indicator_booking.end_time = end_time
		indicator_booking.save()
	return indicator_booking


@retry(stop=stop_after_attempt(1), retry=retry_if_exception_type(OperationalError), reraise=True)
def book_room_serializable(room_id, user, start_time, end_time, sleep_sec=0):
	try:
		with transaction.atomic():
			is_booked = RoomBooking.objects.using("serializable").filter(room_id=room_id, start_time__lt=end_time, end_time__gt=start_time).exists()
			# if between select query and insert query here,
			# another transaction make the insert query, deadlock happens
			if sleep_sec > 0:
				with connections["serializable"].cursor() as cur:
					cur.execute(f"select sleep({sleep_sec})")
			if not is_booked:
				booking = RoomBooking(
					room_id=room_id,
					user=user,
					start_time=start_time,
					end_time=end_time,
				)
				booking.save(using="serializable")
				return booking
			return None
	except OperationalError:
		# deadlock or timeout
		raise


def book_room_no_guard(room_id, user, start_time, end_time, sleep_sec=0):
	with transaction.atomic():
		# `select_for_update` does not lock with empty queryset,
		# so if another transaction commits adding new booking,
		# current one cant lock it aka the `exists` check return False.
		current_room_bookings = RoomBooking.objects.filter(room_id=room_id).select_for_update()
		if sleep_sec > 0:
			with connections["default"].cursor() as cur:
				cur.execute(f"select sleep({sleep_sec})")
		if current_room_bookings.filter(start_time__lt=end_time, end_time__gt=start_time).exists():
			return None
		indicator_booking = RoomBooking(
			room_id=room_id,
			user=user,
		)
		indicator_booking.start_time = start_time
		indicator_booking.end_time = end_time
		indicator_booking.save()
	return indicator_booking
