from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import Http404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from datetime import datetime, timedelta, date
from django.utils import timezone

from .models import Event, Photo, CustomUser
from .forms import PhotoUploadForm, PhotoEditForm

# Create your views here.
def home_view(request):
    current_active_event = None
    recent_event = None
    error_message = None

    try:
        current_active_event = Event.objects.get(is_active=True)
    except Event.DoesNotExist:
        seven_days_ago = timezone.now() - timedelta(days=7)
        recent_event = Event.objects.filter(
            is_active=False,
            end_time__gte=seven_days_ago
            ).order_by('-end_time')
        
        if recent_event.exists():
            recent_event = recent_event.first()
        else:
            recent_event = Event.objects.order_by('-end_time').first()

    if 'kld_email_error' in request.session:
        error_message = request.session.pop('kld_email_error')

    if request.user.is_authenticated:
        user = request.user
        joined_event_code = user.joined_event_code
        event_code_form_error = None

        if request.method == 'POST':
            entered_code = request.POST.get('event_code_input', '').strip()
            if entered_code:
                try:
                    event_to_join = Event.objects.get(event_code=entered_code)
                    if event_to_join.is_active:
                        user.joined_event_code = entered_code
                        user.save()
                        messages.success(request, f"You have joined {event_to_join.name}!")
                        return redirect('photo_gallery')
                    else:
                        event_code_form_error = "This event is not active."
                except Event.DoesNotExist:
                    event_code_form_error = "Invalid event code. Please try again."
            else:
                event_code_form_error = "Please enter an event code."
        
        if joined_event_code:
            try:
                joined_event = Event.objects.get(event_code=joined_event_code)
                if joined_event.is_active:
                    return redirect('photo_gallery')
            except Event.DoesNotExist:
                user.joined_event_code = None
                user.save()
                messages.warning(request, "The event you were previously joined to no longer exists or is invalid. Please contact the administrator.")
        
        context = {
            'is_authenticated_user': True,
            'current_active_event': current_active_event,
            'recent_event': recent_event,
            'event_code_form_error': event_code_form_error,
            'global_error_message': error_message,
        }
        return render(request, 'events_photos/home.html', context)
    else:
        context = {
            'is_authenticated_user': False,
            'current_active_event': current_active_event,
            'recent_event': recent_event,
            'global_error_message': error_message,
        }
        return render(request, 'events_photos/home.html', context)
        
@login_required
def upload_photo_view(request):
    try:
        active_event = Event.objects.get(is_active=True)
    except Event.DoesNotExist:
        messages.error(request, "No active event found. Please contact the administrator.")
        return redirect('home')
    except Event.MultipleObjectsReturned:
        messages.error(request, "Multiple active events found. Please contact the administrator.")
        return redirect('home')

    if request.method == 'POST':
        form = PhotoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            photo = form.save(commit=False)
            photo.event = active_event
            photo.uploaded_by = request.user
            photo.save()
            messages.success(request, "Photo uploaded successfully!")
            return redirect('photo_gallery')
        else:
            messages.error(request, "Error uploading photo. Please try again.")
    else:
        form = PhotoUploadForm()
    
    context = {
        'form': form,
        'active_event': active_event
    }
    return render(request, 'events_photos/upload_photo.html', context)

@login_required
def photo_gallery_view(request):
    active_event = None
    photos_page = []

    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    preset_filter = request.GET.get('preset')

    today = date.today()
    filter_start_date = None
    filter_end_date = None

    if preset_filter:
        if preset_filter == 'today':
            filter_start_date = today
            filter_end_date = today
        elif preset_filter == 'last_7_days':
            filter_start_date = today - timedelta(days=6)
            filter_end_date = today
        elif preset_filter == 'this_month':
            filter_start_date = today.replace(day=1)
            filter_end_date = date(today.year, today.month, 1) + timedelta(days=32)
            filter_end_date = filter_end_date.replace(day=1) - timedelta(days=1)
    elif start_date_str and end_date_str:
        try:
            filter_start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            filter_end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, "Invalid date format. Please use YYYY-MM-DD.")
            filter_start_date = None
            filter_end_date = None
    elif start_date_str:
        try:
            filter_start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            filter_end_date = today
        except ValueError:
            messages.error(request, "Invalid start date format. Please use YYYY-MM-DD.")
            filter_start_date = None
    elif end_date_str:
        try:
            filter_end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            filter_start_date = date(1990, 1, 1)
        except ValueError:
            messages.error(request, "Invalid end date format. Please use YYYY-MM-DD.")
            filter_end_date = None

    try:
        active_event = Event.objects.get(is_active=True)
        all_photos = Photo.objects.filter(event=active_event).order_by('-uploaded_at')

        if filter_start_date:
            all_photos = all_photos.filter(uploaded_at__date__gte=filter_start_date)
        if filter_end_date:
            all_photos = all_photos.filter(uploaded_at__date__lte=filter_end_date)

        photos_per_page = 20
        paginator = Paginator(all_photos, photos_per_page)
        page_number = request.GET.get('page', 1)
        try:
            photos_page = paginator.page(page_number)
        except PageNotAnInteger:
            photos_page = paginator.page(1)
        except EmptyPage:
            photos_page = paginator.page(paginator.num_pages)

    except Event.DoesNotExist:
        messages.error(request, "No active event found. No photos to display.")
    except Event.MultipleObjectsReturned:
        messages.error(request, "Multiple active events found. Please contact the administrator.")
    
    context = {
        'active_event': active_event,
        'photos': photos_page,
        'start_date': start_date_str,
        'end_date': end_date_str,
        'preset_filter': preset_filter,
    }
    return render(request, 'events_photos/photo_gallery.html', context)

@login_required
def edit_photo_view(request, photo_id):
    photo = get_object_or_404(Photo, id=photo_id)
    
    if request.user != photo.uploaded_by:
        messages.error(request, "You are not authorized to edit this photo.")
        return redirect('photo_gallery')

    if request.method == 'POST':
        form = PhotoEditForm(request.POST, instance=photo)
        if form.is_valid():
            form.save()
            messages.success(request, "Photo updated successfully!")
            return redirect('photo_gallery')
        else:
            messages.error(request, "Error updating photo. Please try again.")
    else:
        form = PhotoEditForm(instance=photo)
    
    context = {
        'form': form,
        'photo': photo
    }
    return render(request, 'events_photos/edit_photo.html', context)

@login_required
def delete_photo_view(request, photo_id):
    photo = get_object_or_404(Photo, id=photo_id)
    
    if request.user != photo.uploaded_by:
        messages.error(request, "You are not authorized to delete this photo.")
        return redirect('photo_gallery')
    
    if request.method == 'POST':
        photo.delete()
        messages.success(request, "Photo deleted successfully!")
        return redirect('photo_gallery')
    
    context = {
        'photo': photo
    }
    return render(request, 'events_photos/confirm_delete_photo.html', context)

