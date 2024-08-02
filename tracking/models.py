from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class WorkingHours(models.Model):
    user = models.CharField(max_length=100)  # To store username (use CharField until LDAP is implemented)
    date = models.DateField(default=timezone.now)
    start_time = models.DateTimeField(null=True, blank=True)
    stop_time = models.DateTimeField(null=True, blank=True)
    night_off = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user} - {self.date}"
