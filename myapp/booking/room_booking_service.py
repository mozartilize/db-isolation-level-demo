from datetime import datetime, time
from time import sleep

import pytz
from django.db import IntegrityError, transaction, connection

from .models import RoomBooking


def book_room(room_id, user, start_time, end_time, sleep_sec):
	start_time_in_min_time = datetime.combine(start_time.date(), time(0), pytz.utc)
	end_time_in_max_time = datetime.combine(end_time.date(), time(23, 59, 59, 999999), pytz.utc)
	indicator_booking, created = RoomBooking.objects.get_or_create(
		room_id=room_id,
		start_time=start_time_in_min_time,
		end_time=end_time_in_max_time,
		defaults={"user": user}
	)

	with transaction.atomic():
		current_room_bookings = RoomBooking.objects.filter(room_id=room_id).select_for_update()
		with connection.cursor() as cur:
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


def book_room_fail_version(room_id, user, start_time, end_time, sleep_sec):
	with transaction.atomic():
		# `select_for_update` does not lock with empty queryset,
		# so if another transaction commits adding new booking,
		# current one cant lock it aka the `exists` check return False.
		current_room_bookings = RoomBooking.objects.filter(room_id=room_id).select_for_update()
		with connection.cursor() as cur:
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
