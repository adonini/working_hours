from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from django.contrib.auth.forms import AuthenticationForm
from .forms import LoginForm
from .models import Shift, ShiftType, Break
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from datetime import timedelta

TYPEHOURS = {
    2: 4.5,
    3: 9
}

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

            # Fetch shift history (last 30 days)
            thirty_days_ago = today - timedelta(days=30)
            shifts_history = Shift.objects.filter(user=self.request.user,
                                                  shift_start__gte=thirty_days_ago).order_by('-shift_start') #.exclude(shift_type=ShiftType.objects.get(id=1)) This removes the days off

            # Calculate duration for each shift in hours
            for shift in shifts_history:
                if shift.shift_end:
                    duration_seconds = (shift.shift_end - shift.shift_start).total_seconds()
                    shift.duration_hours = duration_seconds / 3600
                else:
                    shift.duration_hours = None

            # Get shifts for today
            shifts_today = Shift.objects.filter(user=self.request.user, shift_start__date=today).exclude(shift_type=ShiftType.objects.get(id=1))

            # Calculate total hours worked for today
            total_hours_worked_today = sum(
                (shift.shift_end - shift.shift_start).total_seconds()
                for shift in shifts_today if shift.shift_end
            )

            # Calculate total break time for today
            breaks_today = Break.objects.filter(shift__user=self.request.user, break_start__date=today)
            total_breaks_today = sum(
                (brk.break_end - brk.break_start).total_seconds()
                for brk in breaks_today if brk.break_end
            )

            # Adjust total hours worked today by subtracting breaks
            total_hours_worked_today -= total_breaks_today
            total_hours_worked_today /= 3600  # Convert to hours
            total_breaks_today /= 3600  # Convert to hours

            # Calculate the sum of total hours worked and total breaks
            total_worked_and_breaks_today = total_hours_worked_today + total_breaks_today

            # Get shifts for the week
            shifts_week = Shift.objects.filter(user=self.request.user, shift_start__date__range=[start_of_week, end_of_week]).exclude(shift_type=ShiftType.objects.get(id=1))

            # Calculate total hours worked for the week
            total_hours_worked_week = sum(
                (shift.shift_end - shift.shift_start).total_seconds()
                for shift in shifts_week if shift.shift_end
            )

            # Calculate total break time for the week
            breaks_week = Break.objects.filter(shift__user=self.request.user, break_start__date__range=[start_of_week, end_of_week])
            total_breaks_week = sum(
                (brk.break_end - brk.break_start).total_seconds()
                for brk in breaks_week if brk.break_end
            )

            # Adjust total hours worked week by subtracting breaks
            total_hours_worked_week -= total_breaks_week
            total_hours_worked_week /= 3600  # Convert to hours
            total_breaks_week /= 3600  # Convert to hours

            # Calculate the sum of total hours worked and total breaks for the week
            total_worked_and_breaks_week = total_hours_worked_week + total_breaks_week

            # Check for active shift
            active_shift = Shift.objects.filter(user=self.request.user, shift_active=True).last()

            # Check for active break
            active_break = Break.objects.filter(shift=active_shift, break_active=True).last() if active_shift else None

            # Check if the user has set the night as off
            night_off = Shift.objects.filter(user=self.request.user, shift_type=1).last()
            if night_off is not None:
                currentTime = timezone.now()
                startDate = night_off.shift_start.strftime('%Y/%m/%d')
                todayDate = currentTime.strftime('%Y/%m/%d')
                if startDate == todayDate:
                    night_off = True

            # create context
            context['current_datetime'] = now
            context['total_hours_worked_today'] = total_hours_worked_today
            context['total_hours_worked_week'] = total_hours_worked_week
            context['shifts_history'] = shifts_history
            context['active_shift'] = active_shift
            context['total_breaks_today'] = total_breaks_today
            context['total_breaks_week'] = total_breaks_week
            context['active_break'] = active_break
            context['total_worked_and_breaks_today'] = total_worked_and_breaks_today
            context['total_worked_and_breaks_week'] = total_worked_and_breaks_week
            context['night_off'] = night_off
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
        # Create a new Shift object into the model
        shift = Shift.objects.create(
            user=request.user,
            shift_start=timezone.now(),
            shift_active=True
            #end_time=timezone.now() + timezone.timedelta(hours=8),
            #employee="Default Employee"
        )
        # Return data into the template
        data = {
            'shift_id': shift.id,
            'start_time': shift.shift_start.strftime("%Y-%m-%d %H:%M:%S")
            #'end_time': shift.end_time.strftime("%Y-%m-%d %H:%M:%S"),
            #'employee': shift.employee,
        }
        return JsonResponse(data)
    else:
        return render(request, 'your_template.html')


@login_required
def shift_details(request):
    shift = Shift.objects.filter(user=request.user, shift_end__isnull=True).last()
    if not shift:
        return redirect('index')  # Redirect if no active shift is found

    # Calculate the total worked time subtracting break times
    total_worked_time = timezone.now() - shift.shift_start
    total_break_time = sum(
        (break_.break_end - break_.break_start).total_seconds()
        for break_ in Break.objects.filter(shift=shift) if break_.break_end
    )
    total_worked_time -= timedelta(seconds=total_break_time)

    context = {
        'shift': shift,
        'start_time': shift.shift_start.strftime('%Y-%m-%d %H:%M:%S'),
        'total_worked_time': total_worked_time,
        'total_break_time': total_break_time,
        'active_break': Break.objects.filter(shift=shift, break_end__isnull=True).last()
    }
    return render(request, 'shift_details.html', context)


@login_required
def end_shift(request):
    # Find the latest active shift for the user
    shift = Shift.objects.filter(user=request.user, shift_end__isnull=True, shift_active=True).last()
    if shift:
        shift.shift_end = timezone.now()
        delta = shift.shift_end - shift.shift_start
        if delta.total_seconds() <= (TYPEHOURS[2] * 3600) and delta.total_seconds() > 0:
            shift.shift_type = ShiftType.objects.get(id=2)
        else:
            shift.shift_type = ShiftType.objects.get(id=3)

        shift.shift_active = False
        shift.save()

        # Check if there is an ongoing break and end it
        active_breaks = Break.objects.filter(shift=shift, break_end__isnull=True, break_active=True)
        for active_break in active_breaks:
            active_break.break_end = timezone.now()
            active_break.break_active = False
            active_break.save()

        messages.success(request, "You have ended your shift.")
    else:
        messages.warning(request, "No active shift found.")

    return redirect('index')


@login_required
def start_break(request):
    active_shift = Shift.objects.filter(user=request.user, shift_end__isnull=True, shift_active=True).last()
    if active_shift:
        Break.objects.create(shift=active_shift, break_start=timezone.now())
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'failed'}, status=400)


@login_required
def end_break(request):
    active_shift = Shift.objects.filter(user=request.user, shift_end__isnull=True, shift_active=True).last()
    if active_shift:
        active_break = Break.objects.filter(shift=active_shift, break_end__isnull=True, break_active=True).last()
        if active_break:
            active_break.break_end = timezone.now()
            active_break.break_active = False
            active_break.save()
            return redirect('shift_details')  # Redirect to shift_details after resuming work
    return JsonResponse({'status': 'failed'}, status=400)


@login_required
def break_details(request):
    active_shift = get_object_or_404(Shift, user=request.user, shift_end__isnull=True, shift_active=True)
    active_break = Break.objects.filter(shift=active_shift, break_end__isnull=True).last()
    if not active_break:
        return redirect('shift_details')  # Redirect if no active break is found

    context = {
        'active_break': active_break,
        'break_start_time': active_break.break_start.strftime('%Y-%m-%d %H:%M:%S'),
    }
    return render(request, 'break_details.html', context)

@login_required
def night_off(request):
    active_shift = Shift.objects.filter(user=request.user, shift_end__isnull=True, shift_active=True).last()
    if active_shift is None:
        off = Shift.objects.filter(user=request.user, shift_type=ShiftType.objects.get(id=1)).last()
        currentTime = timezone.now()
        if off is not None:
            startDate = off.shift_start.strftime('%Y/%m/%d')
            todayDate = currentTime.strftime('%Y/%m/%d')
            if startDate != todayDate:
                off = Shift.objects.create(
                    user=request.user,
                    shift_start=currentTime,
                    shift_end=currentTime,
                    shift_type = ShiftType.objects.get(id=1),
                    shift_active=False
                )
                messages.success(request, "You have setted your night off.")
            else:
                messages.warning(request, "You already have a shift.")
        else:
            off = Shift.objects.create(
                user=request.user,
                shift_start=currentTime,
                shift_end=currentTime,
                shift_type = ShiftType.objects.get(id=1),
                shift_active=False
            )
            messages.success(request, "You have setted your night off.")

    return redirect('index')

@login_required
def revert_off(request):
    active_shift = Shift.objects.filter(user=request.user, shift_end__isnull=True, shift_active=True).last()
    if active_shift is None:
        off = Shift.objects.filter(user=request.user, shift_type=1).last()
        startDate = off.shift_start.strftime('%Y/%m/%d')
        currentTime = timezone.now()
        todayDate = currentTime.strftime('%Y/%m/%d')
        if startDate == todayDate:
            off.delete()
            return redirect('index')
        else:
            return JsonResponse({'status': 'failed'}, status=400)
        
@login_required
def off_details(request):
    return render(request, 'off_details.html')
