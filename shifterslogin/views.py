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


def logout_user(request):
    logout(request)
    messages.success(request, "You Have Been Logged Out...")
    return redirect('index')


class Index(TemplateView):
    template_name = 'login/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['shift-types'] = ShiftType.objects.all()
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
            shift_start=timezone.now()
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
    shift = Shift.objects.filter(user=request.user, shift_end__isnull=True).last()
    if shift:
        shift.shift_end = timezone.now()
        shift.save()
    return redirect('index')  # TODO: maybe another page instead of back to the home?


def start_break(request):
    # Implement functionality to start a break
    return redirect('home')
