from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import Http404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from datetime import datetime, timedelta, date
from .models import Event, Photo
from .forms import PhotoUploadForm, PhotoEditForm

# Create your views here.
@login_required
def welcome_view(request):
    return render(request, 'events_photos/welcome.html')

@login_required
def upload_photo_view(request):
    try:
        active_event = Event.objects.get(is_active=True)
    except Event.DoesNotExist:
        messages.error(request, "No active event found. Please contact the administrator.")
        return redirect('welcome')
    except Event.MultipleObjectsReturned:
        messages.error(request, "Multiple active events found. Please contact the administrator.")
        return redirect('welcome')

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

