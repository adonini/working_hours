from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.views.generic import TemplateView
from django.contrib.auth.forms import AuthenticationForm
from .forms import LoginForm
from .models import Shift, ShiftType
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from datetime import timedelta


def logout_user(request):
    logout(request)
    messages.success(request, "You Have Been Logged Out...")
    return redirect('index')


class Index(TemplateView):
    template_name = 'login/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['shift_types'] = ShiftType.objects.all()

        if self.request.user.is_authenticated:
            now = timezone.now()
            today = now.date()

            # Define the start and end of the week with Monday as the start and Sunday as the end
            start_of_week = today - timedelta(days=(today.weekday() - 0) % 7)  # Monday is 0
            end_of_week = start_of_week + timedelta(days=6)  # Sunday is the last day of the week

            # Fetch shift history (last 10 items)
            shifts_history = Shift.objects.filter(user=self.request.user).order_by('-shift_start')[:10]
            # Calculate duration for each shift in hours
            for shift in shifts_history:
                if shift.shift_end:
                    duration_seconds = (shift.shift_end - shift.shift_start).total_seconds()
                    shift.duration_hours = duration_seconds / 3600
                else:
                    shift.duration_hours = None
            # Get shifts for today
            shifts_today = Shift.objects.filter(user=self.request.user, shift_start__date=today)

            # Calculate total hours worked and breaks for today
            total_hours_worked_today = sum(
                (shift.shift_end - shift.shift_start).total_seconds()
                for shift in shifts_today if shift.shift_end
            )
            total_hours_worked_today /= 3600  # Convert to hours

            # total_hours_break_today = sum(
            #     (shift.break_end - shift.break_start).total_seconds()
            #     for shift in shifts_today if shift.break_end and shift.break_start
            # )
            # total_hours_break_today /= 3600  # Convert to hours

            # Get shifts for the week
            shifts_week = Shift.objects.filter(user=self.request.user, shift_start__date__range=[start_of_week, end_of_week])

            # Calculate total hours worked and breaks for the week
            total_hours_worked_week = sum(
                (shift.shift_end - shift.shift_start).total_seconds()
                for shift in shifts_week if shift.shift_end
            )
            total_hours_worked_week /= 3600  # Convert to hours

            # total_hours_break_week = sum(
            #     (shift.break_end - shift.break_start).total_seconds()
            #     for shift in shifts_week if shift.break_end and shift.break_start
            # )
            # total_hours_break_week /= 3600  # Convert to hours

            # Check for active shift
            active_shift = Shift.objects.filter(user=self.request.user, shift_active=True).last()

            # create context
            context['current_datetime'] = now
            context['total_hours_worked_today'] = total_hours_worked_today
            #context['total_hours_break_today'] = total_hours_break_today
            context['total_hours_worked_week'] = total_hours_worked_week
            #context['total_hours_break_week'] = total_hours_break_week
            context['shifts_history'] = shifts_history
            context['active_shift'] = active_shift
        return context


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('index')
    else:
        form = LoginForm()
    return render(request, 'login/login.html', {'form': form})


def start_shift(request):
    if request.method == "POST":
        # Crear un nuevo registro en el modelo Shift
        shift = Shift.objects.create(
            user=request.user,
            shift_start=timezone.now(),
            shift_active=True
            #end_time=timezone.now() + timezone.timedelta(hours=8),
            #employee="Default Employee"
        )
        # Devolver datos al template
        data = {
            'shift_id': shift.id,
            'start_time': shift.shift_start.strftime("%Y-%m-%d %H:%M:%S")
            #'end_time': shift.end_time.strftime("%Y-%m-%d %H:%M:%S"),
            #'employee': shift.employee,
        }
        return JsonResponse(data)
    else:
        return render(request, 'your_template.html')


def shift_details(request):
    shift = Shift.objects.filter(user=request.user, shift_end__isnull=True).last()
    if not shift:
        return redirect('index')  # Redirect if no active shift is found
    context = {
        'shift': shift,
        'start_time': shift.shift_start.strftime('%Y-%m-%d %H:%M:%S'),
    }
    return render(request, 'shift_details.html', context)


def end_shift(request):
    shift = Shift.objects.filter(user=request.user, shift_end__isnull=True, shift_active=True).last()
    if shift:
        shift.shift_end = timezone.now()
        shift.shift_active = False  # Set the active state to false
        shift.save()
        messages.success(request, "You have ended your shift.")
    return redirect('index')  # TODO: maybe another page instead of back to the home?


def start_break(request):
    # Implement functionality to start a break
    return redirect('home')
