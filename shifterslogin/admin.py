from django.contrib import admin
from django.contrib.auth.models import User
from django.db.models import Count, Sum, F, ExpressionWrapper, fields
from django.db.models.functions import TruncDay
from django.utils import timezone
from django.urls import path
from django.shortcuts import render
from django.http import JsonResponse
import json
from .models import ShiftType, Shift, Break
from django.core.serializers.json import DjangoJSONEncoder
import logging

# Get a logger instance
logger = logging.getLogger('myapp')


admin.site.register(ShiftType)
admin.site.register(Shift)
admin.site.register(Break)


def custom_admin_index(request):
    # Calculate the number of users with at least one shift
    users_with_shifts = User.objects.annotate(shift_count=Count('shift')).filter(shift_count__gt=0).count()

    # Calculate the time range for the last 30 days
    now = timezone.now()
    end_date = now.date()
    start_date = end_date - timezone.timedelta(days=30)

    # Initialize chart data
    chart_data = []

    if request.method == 'POST':
        # Handle date range filtering
        data = json.loads(request.body)
        start_date = data.get('start_date')
        end_date = data.get('end_date')

        if start_date and end_date:
            start_date = timezone.datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = timezone.datetime.strptime(end_date, '%Y-%m-%d').date()

            # Calculate the number of days and weeks in the range
            days_count = (end_date - start_date).days + 1
            weeks_count = days_count / 7

            # Aggregate total hours worked per user
            shifts = Shift.objects.filter(
                shift_start__gte=start_date,
                shift_end__lte=end_date
            ).values(
                'user__username'
            ).annotate(
                total_hours=Sum(
                    ExpressionWrapper(F('shift_end') - F('shift_start'), output_field=fields.DurationField())
                )
            )

            chart_data = [
                {
                    'username': shift['user__username'],
                    'avg_per_day': shift['total_hours'].total_seconds() / (3600 * days_count),
                    'avg_per_week': shift['total_hours'].total_seconds() / (3600 * weeks_count)
                }
                for shift in shifts
            ]

            return JsonResponse({'chart_data': chart_data}, encoder=DjangoJSONEncoder)

    # Provide default chart data for initial load
    shifts = Shift.objects.filter(
        shift_start__gte=start_date,
        shift_end__lte=end_date
    ).values(
        'user__username'
    ).annotate(
        total_hours=Sum(
            ExpressionWrapper(F('shift_end') - F('shift_start'), output_field=fields.DurationField())
        )
    )

    days_count = (end_date - start_date).days + 1
    weeks_count = days_count / 7

    chart_data = [
        {
            'username': shift['user__username'],
            'avg_per_day': shift['total_hours'].total_seconds() / (3600 * days_count),
            'avg_per_week': shift['total_hours'].total_seconds() / (3600 * weeks_count)
        }
        for shift in shifts
    ]

    as_json = json.dumps(chart_data, cls=DjangoJSONEncoder)

    # Pass the info to the template
    extra_context = {
        'users_with_shifts': users_with_shifts,
        'users_recent_shifts': User.objects.filter(shift__shift_start__gte=timezone.now() - timezone.timedelta(days=3)).distinct(),
        'chart_data': as_json
    }

    return render(request, 'admin/index.html', extra_context)


# Register the custom admin index view
admin_urls = admin.site.get_urls()
admin.site.get_urls = lambda: [path('', custom_admin_index)] + admin_urls
