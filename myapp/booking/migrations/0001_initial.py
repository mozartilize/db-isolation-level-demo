# Generated by Django 4.0.3 on 2022-04-06 15:25

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='RoomBooking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('room_id', models.CharField(db_index=True, max_length=10)),
                ('user', models.CharField(db_index=True, max_length=10)),
                ('start_time', models.DateTimeField()),
                ('end_time', models.DateTimeField()),
            ],
            options={
                'db_table': 'room_bookings',
                'unique_together': {('room_id', 'start_time', 'end_time')},
            },
        ),
    ]
