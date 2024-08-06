from django.db.models.signals import post_migrate
from django.dispatch import receiver
from .models import ShiftType
from django.contrib.auth.models import User
import logging

logger = logging.getLogger(__name__)

@receiver(post_migrate)
def create_default_entries(sender, **kwargs):
    if sender.name == 'shifterslogin':  # app name
        ShiftTypes_entries = [
            {'name': 'Off'},
            {'name': 'Half-night'},
            {'name': 'Full-night'},
        ]

        if not User.objects.filter(username='user').exists():
            User.objects.create_superuser(
                username='user',
                email='defaultuser@example.com',
                password='1234'
            )
            print("Default user created")
        
        for entry in ShiftTypes_entries:
            ShiftType.objects.get_or_create(**entry)