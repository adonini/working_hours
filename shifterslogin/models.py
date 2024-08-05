from django.db import models
from django.contrib.auth.models import User


class ShiftType(models.Model):
    name = models.CharField(max_length=200)

    class Meta:
        db_table = 'shiftTypes'

    def __str__(self):
        return self.name


class Shift(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    shift_type = models.ForeignKey(ShiftType, on_delete=models.SET_NULL, blank=True, null=True)
    shift_start = models.DateTimeField(blank=True, null=True)
    shift_end = models.DateTimeField(blank=True, null=True)
    shift_active = models.BooleanField(default=True)  # New flag to indicate active shift. Default True when shift starts

    class Meta:
        db_table = 'shifts'


class Break(models.Model):
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE, related_name='breaks')
    break_start = models.DateTimeField()
    break_end = models.DateTimeField(null=True, blank=True)
    break_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'breaks'
