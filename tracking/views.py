from django.shortcuts import render, redirect
from django.utils import timezone
from .models import WorkingHours
from django.contrib.auth.decorators import login_required


#@login_required
def main(request):
    if request.method == 'POST':
        if 'start' in request.POST:
            working_hours, created = WorkingHours.objects.get_or_create(
                user=request.user.username,
                date=timezone.now().date(),
                defaults={'start_time': timezone.now()}
            )
            if not created:
                working_hours.start_time = timezone.now()
                working_hours.save()
        elif 'stop' in request.POST:
            working_hours = WorkingHours.objects.filter(
                user=request.user.username,
                date=timezone.now().date(),
                night_off=False
            ).last()
            if working_hours and working_hours.start_time and not working_hours.stop_time:
                working_hours.stop_time = timezone.now()
                working_hours.save()
        elif 'night_off' in request.POST:
            WorkingHours.objects.create(
                user=request.user.username,
                date=timezone.now().date(),
                night_off=True
            )
        return redirect('main')

    return render(request, 'tracking/main.html')
