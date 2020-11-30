from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.conf import settings
from django.contrib import messages
from .forms import AppointmentForm
from appointments.models import AppointmentsCalendar
from products.models import Product
from .utils import Calendar, convertToDatetime, get_date, prev_month, next_month, get_footer
from datetime import datetime
from django.utils.safestring import mark_safe
from django.views import generic
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required


def appointments(request, product_id):
    """ A view to request an appointment at a specified date & time """
    appointments = list(AppointmentsCalendar.objects.all().values())
    if request.method == 'GET':
        username = request.user.username
        email = request.user.email
        form = AppointmentForm(initial={'name': username, 'email': email})
    else:
        currentMonth = datetime.now().month
        currentYear = datetime.now().date().strftime('%y')
        if currentMonth < 3:
            minMonth = currentMonth + 10
        else:
            minMonth = currentMonth - 2

        minDate = f'{minMonth}/{currentYear}'
        day = datetime.now().date().strftime('%d')
        form = AppointmentForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            cust_email = form.cleaned_data['email']
            message = form.cleaned_data['message']
            date = form.cleaned_data['date']
            time = form.cleaned_data['time']
            host_email = settings.DEFAULT_FROM_EMAIL
            for item in appointments:
                if item['date_str'][3:8] == minDate:
                    if int(item['date_str'][0:2]) < int(day):
                        AppointmentsCalendar(id=item['id']).delete()
                    elif item['time'] == time and item['date_str'] == date:
                        messages.error(request, 'Sorry, that appointment time has already been taken. Please select another time.')
                        return redirect(reverse('appointments', args=[product_id]))
            appointment_details = {
                'name': name,
                'cust_email': cust_email,
                'message': message,
                'date': date,
                'time': time,
                'host_email': host_email,
            }
            request.session['appointment_id'] = product_id
            request.session['appointment_details'] = appointment_details
            return redirect(reverse('purchase_appointment'))
    return render(request, 'appointments/appointments.html', {'form': form})


def purchaseAppointment(request):
    """ A view to confirm appointment details then add to shopping basket """
    if not request.user.is_authenticated:
        messages.error(request, 'Sorry, only registered users can purchase an appointment.')
        return redirect(reverse('appointments'))

    appointment = get_object_or_404(Product, pk=request.session['appointment_id'])

    context = {
        'appointment': appointment,
        'appointment_details': request.session['appointment_details']
    }

    return render(request, 'appointments/purchase_appointment.html', context)


class appointmentCalendar(generic.ListView):
    model = AppointmentsCalendar
    template_name = 'appointments/appointment_calendar.html'
    success_url = reverse_lazy("appointment_calendar")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        d = get_date(self.request.GET.get('month', None))
        cal = Calendar(d.year, d.month)
        html_cal = cal.formatmonth(withyear=True)
        html_cal += get_footer()
        context['calendar'] = mark_safe(html_cal)
        context['prev_month'] = prev_month(d)
        context['next_month'] = next_month(d)
        return context


@login_required
def appointmentDetails(request,  appointment_details_id):
    """ Displays individual calendar appointment details """
    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only users with admin privileges can do that.')
        return redirect(reverse('home'))

    appointment_details = AppointmentsCalendar.objects.filter(pk=appointment_details_id).values()[0]

    context = {
        'appointment_details': appointment_details,
    }

    return render(request, 'appointments/appointment_details.html', context)


@login_required
def confirmAppointment(request, appointment_details_id):
    """ Allows superuser to confirms individual calendar appointment details """
    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only users with admin privileges can do that.')
        return redirect(reverse('home'))

    appointment_details = AppointmentsCalendar.objects.filter(pk=appointment_details_id)
    appointment_details.update(confirmed=True)
    appointment = appointment_details.values()[0]
    name = appointment['name']
    messages.success(request, f'Appointment for {name} has been confirmed')

    context = {
        'appointment_details': appointment,
    }

    return render(request, 'appointments/appointment_details.html', context)


@login_required
def updateAppointment(request, appointment_details_id):
    """ Allows superuser to update individual calendar appointment details """
    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only users with admin privileges can do that.')
        return redirect(reverse('home'))

    appointment_details = AppointmentsCalendar.objects.filter(pk=appointment_details_id)
    if request.method == 'GET':
        appointment = appointment_details.values()[0]
        name = appointment['name']
        email = appointment['email']
        message = appointment['message']
        date_str = appointment['date_str']
        time = appointment['time']
        form = AppointmentForm(initial={'name': name, 'email': email, 'message': message, 'date_str': date_str, 'time': time})
    else:
        form = AppointmentForm(request.POST)
        appointment = {}
        if form.is_valid():
            appointment['name'] = form.cleaned_data['name']
            appointment['email'] = form.cleaned_data['email']
            appointment['message'] = form.cleaned_data['message']
            appointment['date_str'] = form.cleaned_data['date']
            appointment['date'] = convertToDatetime(appointment['date_str'])
            appointment['time'] = form.cleaned_data['time']
            messages.success(request, 'The selected appointment details have been updated.')
            appointment_details.update(**appointment)
        return redirect(reverse('appointment_details', args=[appointment_details_id]))
    return render(request, 'appointments/update_appointment.html', {'form': form})


@login_required
def deleteAppointment(request,  appointment_details_id):
    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only users with admin privileges can do that.')
        return redirect(reverse('home'))

    """ Allows superuser to delete individual calendar appointment """
    appointment = AppointmentsCalendar.objects.filter(pk=appointment_details_id)
    appointment_details = appointment.values()[0]
    appointment.delete()
    messages.success(request, 'The selected appointment details have been deleted.')

    context = {
        'appointment_details': appointment_details,
    }

    return render(request, 'appointments/appointment_details.html', context)
