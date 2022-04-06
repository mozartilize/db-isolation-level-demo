from django.db.models import Model, CharField, DateTimeField


class RoomBooking(Model):
	room_id = CharField(max_length=10, db_index=True)
	user = CharField(max_length=10, db_index=True)
	start_time = DateTimeField()
	end_time = DateTimeField()

	class Meta:
		db_table = "room_bookings"
		unique_together = [
			("room_id", "start_time", "end_time")
		]