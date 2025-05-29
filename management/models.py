from django.db import models
import os
import random
import string
class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Model(models.Model):
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name="models")
    name = models.CharField(max_length=100)

    class Meta:
        unique_together = ('brand', 'name')  # Ensure models are unique within each brand

    def __str__(self):
        return self.name

class SubModel(models.Model):
    model = models.ForeignKey(Model, on_delete=models.CASCADE, related_name="submodels", null=True, blank=True)
    name = models.CharField(max_length=100)

    class Meta:
        unique_together = ('model', 'name')

    def __str__(self):
        return self.name

class YearRange(models.Model):
    sub_model = models.ForeignKey(SubModel, on_delete=models.CASCADE, related_name="year_ranges")
    year_start = models.PositiveSmallIntegerField()
    year_end = models.PositiveSmallIntegerField()

    class Meta:
        unique_together = ('sub_model', 'year_start', 'year_end')

    def __str__(self):
        return f" ({self.year_start} - {self.year_end})"

class MasterSetting(models.Model):
    CATEGORY_CHOICES = [
        ('Channel', 'Channel'),
        ('Country', 'Country'),
        ('Person', 'Person'),
        ('Case Type', 'Case Type'),
        ('Series', 'Series'),
        ('Material', 'Material'),
    ]

    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    name = models.CharField(max_length=100, unique=True)
    class Meta:
        unique_together = ('category', 'name')

    def __str__(self):
        return self.name

    
def generate_complaint_id():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
class Complaint(models.Model):
    complaint_id = models.CharField(primary_key=True, max_length=10, unique=True, default=generate_complaint_id)
    date = models.DateField(auto_now_add=False)
    channel = models.ForeignKey(
        'management.MasterSetting', 
        on_delete=models.SET_NULL, 
        null=True, 
        limit_choices_to={'category': 'Channel'}, 
        related_name="complaints_as_channel"
    )
    country = models.ForeignKey(
        'management.MasterSetting', 
        on_delete=models.SET_NULL, 
        null=True, 
        limit_choices_to={'category': 'Country'}, 
        related_name="complaints_as_country"
    )
    person = models.ForeignKey(
        'management.MasterSetting', 
        on_delete=models.SET_NULL, 
        null=True, 
        limit_choices_to={'category': 'Person'}, 
        related_name="complaints_as_person"
    )
    case_type = models.ForeignKey(
        'management.MasterSetting', 
        on_delete=models.SET_NULL, 
        null=True, 
        limit_choices_to={'category': 'Case Type'}, 
        related_name="complaints_as_case_type"
    )
    series = models.ForeignKey(
        'management.MasterSetting', 
        on_delete=models.SET_NULL, 
        null=True, 
        limit_choices_to={'category': 'Series'}, 
        related_name="complaints_as_series"
    )
    material = models.ForeignKey(
        'management.MasterSetting', 
        on_delete=models.SET_NULL, 
        null=True, 
        limit_choices_to={'category': 'Material'}, 
        related_name="complaints_as_material"
    )
    brand = models.ForeignKey('management.Brand', on_delete=models.SET_NULL, null=True)
    model = models.ForeignKey('management.Model', on_delete=models.SET_NULL, null=True)
    sub_model = models.ForeignKey('management.SubModel', on_delete=models.SET_NULL, null=True, blank=True)
    year = models.ForeignKey('management.YearRange', on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=10, choices=[('Active', 'Active'), ('Inactive', 'Inactive')], default='Active')
    complaint_description = models.TextField()
    batch_order = models.CharField(max_length=100)
    justification_from_factory = models.TextField(blank=True, null=True)
    action_from_factory = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)    

    def __str__(self):
        return self.complaint_id

def media_upload_path(instance, filename):
    return f'complaint_media/complaint_{instance.complaint.complaint_id}/{filename}'

class ComplaintMedia(models.Model):
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE, related_name='media_files')
    file = models.FileField(upload_to=media_upload_path)

    def __str__(self):
        return os.path.basename(self.file.name)
    

