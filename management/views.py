from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Complaint
from django.http import JsonResponse
from .forms import ComplaintForm
from .models import Brand, Model, SubModel, YearRange
from .models import ComplaintMedia
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import Brand, Model, SubModel, YearRange, ComplaintMedia
from .forms import CarDetailsForm
from django.contrib import messages
import os
from django.db.models import Q
from .models import Complaint, Brand
from django.utils.dateparse import parse_date
from collections import Counter
from django.db.models import Count

@login_required
def index(request):
    return render(request, 'management/index.html')


@login_required

def add_car_details(request):
    show_duplicate_modal = False  # Flag for template

    if request.method == "POST":
        form = CarDetailsForm(request.POST)
        if form.is_valid():
            brand_name = form.cleaned_data["brand_name"].strip()
            model_name = form.cleaned_data["model_name"].strip()
            sub_model_name = form.cleaned_data["sub_model_name"].strip() or "-"
            year_start = form.cleaned_data["year_start"]
            year_end = form.cleaned_data["year_end"]

            brand, _ = Brand.objects.get_or_create(name=brand_name)
            model, _ = Model.objects.get_or_create(brand=brand, name=model_name)

            sub_model = None
            if sub_model_name:
                sub_model, _ = SubModel.objects.get_or_create(model=model, name=sub_model_name)

            # Check for duplicates
            # Check for year range overlap
            conflicting_year = YearRange.objects.filter(
                sub_model=sub_model,
                year_start__lte=year_end,
                year_end__gte=year_start
            ).first()


            if conflicting_year:
                show_duplicate_modal = True
                conflicting_car = {
                    "brand": brand.name,
                    "model": model.name,
                    "sub_model": sub_model.name if sub_model else "-",
                    "year_start": conflicting_year.year_start,
                    "year_end": conflicting_year.year_end
                    }

    else:
        form = CarDetailsForm()

    # Fetch existing car data for display
    car_data = []
    for brand in Brand.objects.prefetch_related('models__submodels__year_ranges').all():
        for model in brand.models.all():
            for sub_model in model.submodels.all():
                for year_range in sub_model.year_ranges.all():
                    car_data.append({
                        "id": year_range.id,
                        "brand": brand.name,
                        "model": model.name,
                        "sub_model": sub_model.name,
                        "year_start": year_range.year_start,
                        "year_end": year_range.year_end
                    })
        for year_range in YearRange.objects.filter(sub_model__isnull=True):
            car_data.append({
                "id": year_range.id,
                "brand": brand.name,
                "model": model.name,
                "sub_model": "(No Sub-Model)",
                "year_start": year_range.year_start,
                "year_end": year_range.year_end
            })

    return render(request, 'management/add_car_details.html', {
        'form': form,
        'car_data': car_data,
        'show_duplicate_modal': show_duplicate_modal,
        'conflicting_car': conflicting_car if show_duplicate_modal else None
    })


@login_required
def delete_car_detail(request, year_range_id):
    year_range = get_object_or_404(YearRange, id=year_range_id)
    year_range.delete()
    return redirect('add_car_details')


from django.shortcuts import render, redirect, get_object_or_404
from .models import MasterSetting
from .forms import MasterSettingForm

@login_required
def master_settings(request):
    if request.method == "POST":
        form = MasterSettingForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('master_settings')
    else:
        form = MasterSettingForm()

    # Fetch existing master settings, grouped by category
    master_settings = {}
    for category, _ in MasterSetting.CATEGORY_CHOICES:
        master_settings[category] = MasterSetting.objects.filter(category=category)

    return render(request, 'management/master_settings.html', {
        'form': form,
        'master_settings': master_settings
    })

@login_required
def delete_master_setting(request, setting_id):
    setting = get_object_or_404(MasterSetting, id=setting_id)
    setting.delete()
    return redirect('master_settings')



def add_complaint(request):
    if request.method == 'POST':
        form = ComplaintForm(request.POST)
        if form.is_valid():
            complaint = form.save()

            # Save each uploaded file
            for uploaded_file in request.FILES.getlist('media_files'):
                ComplaintMedia.objects.create(
                    complaint=complaint,
                    file=uploaded_file
                )

            return redirect('complaint_list')
    else:
        form = ComplaintForm()
    return render(request, 'management/add_complaint.html', {'form': form})

@login_required
def get_models(request, brand_id):
    models = Model.objects.filter(brand_id=brand_id).values('id', 'name')
    return JsonResponse(list(models), safe=False)

def get_sub_models(request, model_id):
    sub_models = SubModel.objects.filter(model_id=model_id).values('id', 'name')
    return JsonResponse(list(sub_models), safe=False)

def get_year_ranges(request, sub_model_id):
    year_ranges = YearRange.objects.filter(sub_model_id=sub_model_id).values('id', 'year_start', 'year_end')
    return JsonResponse([{'id': yr['id'], 'range': f"{yr['year_start'] % 100}-{yr['year_end'] % 100}"} for yr in year_ranges], safe=False)

@login_required

def complaint_list(request):
    complaints = Complaint.objects.all()
    search_query = request.GET.get('search', '')
    search_by = request.GET.get('search_by', 'complaint_id')
    selected_brand = request.GET.get('brand')
    selected_country = request.GET.get('country')
    selected_status = request.GET.get('status')
    selected_channel = request.GET.get('channel')
    selected_case_type = request.GET.get('case_type')
    selected_person = request.GET.get('person')

    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')

    if search_query:
        filter_kwargs = {f'{search_by}__icontains': search_query}
        complaints = complaints.filter(**filter_kwargs)
    if selected_status:
        complaints = complaints.filter(status=selected_status)
    if selected_channel:
        complaints = complaints.filter(channel=selected_channel)
    if selected_case_type:
        complaints = complaints.filter(case_type=selected_case_type)
    if selected_person:
        complaints = complaints.filter(person=selected_person) 

    if selected_brand:
        complaints = complaints.filter(brand_id=selected_brand)

    if selected_country:
        complaints = complaints.filter(country=selected_country)

    if from_date:
        complaints = complaints.filter(date__gte=parse_date(from_date))

    if to_date:
        complaints = complaints.filter(date__lte=parse_date(to_date))

    brands = Brand.objects.all()
    countries = MasterSetting.objects.filter(id__in=Complaint.objects.values_list('country', flat=True).distinct())
    channels = MasterSetting.objects.filter(id__in=Complaint.objects.values_list('channel', flat=True).distinct())
    case_types = MasterSetting.objects.filter(id__in=Complaint.objects.values_list('case_type', flat=True).distinct())
    persons = MasterSetting.objects.filter(id__in=Complaint.objects.values_list('person', flat=True).distinct())
    statuses = Complaint.objects.values_list('status', flat=True).distinct()

    # Status Pie Data
    status_qs = complaints.values('status').annotate(count=Count('status'))
    status_labels = [entry['status'] for entry in status_qs]
    status_data = [entry['count'] for entry in status_qs]

    # Case Type Pie Data
    case_type_qs = complaints.values('case_type__name').annotate(count=Count('case_type'))
    case_type_labels = [entry['case_type__name'] for entry in case_type_qs]
    case_type_data = [entry['count'] for entry in case_type_qs]

    # Country Pie Data
    country_qs = complaints.values('country__name').annotate(count=Count('country'))
    country_labels = [entry['country__name'] for entry in country_qs]
    country_data = [entry['count'] for entry in country_qs]

    return render(request, 'management/complaint_list.html', {
        'complaints': complaints,
        'status_labels': status_labels,
        'status_data': status_data,
        'case_type_labels': case_type_labels,
        'case_type_data': case_type_data,
        'country_labels': country_labels,
        'country_data': country_data,
        'search_query': search_query,
        'search_by': search_by,
        'selected_brand': selected_brand,
        'selected_country': selected_country,
        'selected_status': selected_status,
        'selected_channel': selected_channel,
        'selected_case_type': selected_case_type,
        'selected_person': selected_person,
        'selected_status': selected_status,
        'from_date': from_date,
        'to_date': to_date,
        'brands': brands,
        'countries': countries,
        'channels': channels,
        'case_types': case_types,
        'persons': persons,
        'statuses': statuses,
    })



@login_required
def edit_complaint(request, complaint_id):
    complaint = get_object_or_404(Complaint, complaint_id=complaint_id)

    if request.method == 'POST':
        form = ComplaintForm(request.POST, request.FILES, instance=complaint)
        if form.is_valid():
            form.save()

            # Delete selected media
            media_to_delete = request.POST.getlist('delete_media')
            for media_id in media_to_delete:
                media = ComplaintMedia.objects.get(id=media_id)
                media.file.delete()  # delete from storage
                media.delete()

            # Save new uploaded media
            for file in request.FILES.getlist('media'):
                ComplaintMedia.objects.create(complaint=complaint, file=file)

            return redirect('complaint_list')
    else:
        form = ComplaintForm(instance=complaint)

    media_files = complaint.media_files.all()
    return render(request, 'management/edit_complaint.html', {
        'form': form,
        'complaint': complaint,
        'media_files': media_files,
    })

def delete_complaint(request, complaint_id):
    complaint = get_object_or_404(Complaint, pk=complaint_id)
    complaint.delete()
    return redirect('complaint_list')


def delete_media(request, pk):
    media = get_object_or_404(ComplaintMedia, pk=pk)
    complaint_id = media.complaint.batch_order
    media.file.delete()
    media.delete()
    return redirect('edit_complaint', pk=complaint_id)

