# Generated by Django 4.1.3 on 2022-11-24 19:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('beachreservation', '0003_alter_umbrellareservation_number_of_seats'),
    ]

    operations = [
        migrations.AlterField(
            model_name='umbrellareservation',
            name='reservation_price',
            field=models.DecimalField(decimal_places=2, max_digits=6),
        ),
    ]