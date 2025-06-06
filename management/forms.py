from django import forms
from .models import Complaint, ComplaintMedia

class CarDetailsForm(forms.Form):
    layout_code = forms.CharField(label="Layout Code", max_length=100)
    brand_name = forms.CharField(label="Brand Name", max_length=100)
    model_name = forms.CharField(label="Model Name", max_length=100)
    sub_model_name = forms.CharField(label="Sub-Model Name", max_length=100, required=False,)
    year_start = forms.IntegerField(label="Year Start", min_value=1900, max_value=2100)
    year_end = forms.IntegerField(label="Year End", min_value=1900, max_value=2100)
    number_of_seats = forms.IntegerField(label="Number of Seats", min_value=1)
    number_of_doors = forms.IntegerField(label="Number of Doors", min_value=1)
    

    def clean(self):
        cleaned_data = super().clean()
        for field in ['brand_name', 'model_name', 'sub_model_name', 'layout_code']:
            if field in cleaned_data and isinstance(cleaned_data[field], str):
                cleaned_data[field] = cleaned_data[field].strip()
        year_start = cleaned_data.get("year_start")
        year_end = cleaned_data.get("year_end")
        
        if year_start and year_end and year_start > year_end:
            self.add_error("year_end", "Year End must be greater than or equal to Year Start.")
        
        return cleaned_data

from django import forms
from .models import MasterSetting

class MasterSettingForm(forms.ModelForm):
    class Meta:
        model = MasterSetting
        fields = ['category', 'name']

from django import forms
from .models import Complaint, MasterSetting, Brand, Model, SubModel, YearRange

class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = [
            'complaint_id','date', 'channel', 'country', 'person', 'case_category','case_sub_category', 'series', 'material', 
            'brand', 'model', 'sub_model', 'year', 'status', 'sku', 
            'complaint_description', 'batch_order', 
            'justification_from_factory', 'action_from_factory'
        ]
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['brand'].queryset = Brand.objects.all()
        self.fields['model'].queryset = Model.objects.none()
        self.fields['sub_model'].queryset = SubModel.objects.none()
        self.fields['year'].queryset = YearRange.objects.none()
        self.fields['sku'].choices = [(sku.id, f"{sku.code} - {sku.description}") for sku in SKU.objects.all()]

        if 'brand' in self.data:
            try:
                brand_id = int(self.data.get('brand'))
                self.fields['model'].queryset = Model.objects.filter(brand_id=brand_id)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['model'].queryset = Model.objects.filter(brand=self.instance.brand)
        if 'model' in self.data:
            try:
                model_id = int(self.data.get('model'))
                self.fields['sub_model'].queryset = SubModel.objects.filter(model_id=model_id)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['sub_model'].queryset = SubModel.objects.filter(model=self.instance.model)
        if 'sub_model' in self.data:
            try:
                sub_model_id = int(self.data.get('sub_model'))
                self.fields['year'].queryset = YearRange.objects.filter(sub_model_id=sub_model_id)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['year'].queryset = YearRange.objects.filter(sub_model=self.instance.sub_model)

# forms.py
from django import forms

class UploadCSVForm(forms.Form):
    csv_file = forms.FileField(label="Upload CSV File")


from .models import SKU
from django import forms
class SKUForm(forms.ModelForm):
    class Meta:
        model = SKU
        fields = ['code', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class SKUUploadForm(forms.Form):
    csv_file = forms.FileField(label="Upload CSV File")
