import datetime
import decimal

from dateutil.relativedelta import relativedelta
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from decimal import *
import beachreservation.utils as utils


# Create your models here.
class UmbrellaReservation(models.Model):
    customer = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    number_of_seats = models.PositiveIntegerField(
        validators=[MinValueValidator(utils.MIN_SEAT_UMBRELLA), MaxValueValidator(utils.MAX_SEAT_UMBRELLA)])

    # reservation_start_date = models.DateField(validators=[MinValueValidator(datetime.date.today()), MaxValueValidator(datetime.date.today() + relativedelta(months=utils.MAX_FUTURE_START_DATE_IN_MONTH))])
    # reservation_end_date = models.DateField(validators=[MinValueValidator(datetime.date.today()), MaxValueValidator(datetime.date.today() + relativedelta(months=utils.MAX_FUTURE_END_DATE_IN_MONTH))]) # reservation_start_date = models.DateField(validators=[MinValueValidator(datetime.date.today()), MaxValueValidator(datetime.date.today() + relativedelta(months=utils.MAX_FUTURE_START_DATE_IN_MONTH))])
    reservation_start_date = models.DateField()
    reservation_end_date = models.DateField()

    reserved_umbrella_id = models.PositiveIntegerField(
        validators=[MinValueValidator(utils.MIN_UMBRELLA_ID), MaxValueValidator(utils.MAX_UMBRELLA_ID)])

    @property
    def reservation_price(self):
        decimal.getcontext().prec = 4
        booked_days = (self.reservation_end_date - self.reservation_start_date).days + 1
        return Decimal(f"{utils.UMBRELLA_BASE_COST}") + 10 * self.number_of_seats * booked_days

    def validate_end_date_after_start_date(self):
        if self.reservation_start_date > self.reservation_end_date:
            raise ValidationError({'reservation_end_date': "End date must be after start date"})

    def validate_overlapping_reservations(self):
        reservations = UmbrellaReservation.objects.all().filter(reserved_umbrella_id=self.reserved_umbrella_id)
        for res in reservations:
            if (res.reservation_start_date <= self.reservation_end_date) and (res.reservation_end_date >= self.reservation_start_date) and (res.id != self.id):
                raise ValidationError(f"Already present a reservation for start:{self.reservation_start_date} end:{self.reservation_end_date}")

    # serializers does not call this method, call it directly
    def clean(self):
        super(UmbrellaReservation, self).clean()
        self.validate_end_date_after_start_date()
        self.validate_overlapping_reservations()

    def __str__(self) -> str:
        return f"{self.id}: {self.customer} from {self.reservation_start_date} to {self.reservation_end_date}"
