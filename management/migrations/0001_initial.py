# Generated by Django 5.2 on 2025-06-01 06:39

import django.db.models.deletion
import management.models
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Brand',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Complaint',
            fields=[
                ('complaint_id', models.CharField(default=management.models.generate_complaint_id, max_length=10, primary_key=True, serialize=False, unique=True)),
                ('date', models.DateField()),
                ('status', models.CharField(choices=[('Active', 'Active'), ('Inactive', 'Inactive')], default='Active', max_length=10)),
                ('complaint_description', models.TextField()),
                ('batch_order', models.CharField(max_length=100)),
                ('justification_from_factory', models.TextField(blank=True, null=True)),
                ('action_from_factory', models.TextField(blank=True, null=True)),
                ('brand', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='management.brand')),
            ],
        ),
        migrations.CreateModel(
            name='ComplaintMedia',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to=management.models.media_upload_path)),
                ('complaint', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='media_files', to='management.complaint')),
            ],
        ),
        migrations.CreateModel(
            name='MasterSetting',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.CharField(choices=[('Channel', 'Channel'), ('Country', 'Country'), ('Person', 'Person'), ('Case Type', 'Case Type'), ('Series', 'Series'), ('Material', 'Material')], max_length=50)),
                ('name', models.CharField(max_length=100, unique=True)),
            ],
            options={
                'unique_together': {('category', 'name')},
            },
        ),
        migrations.AddField(
            model_name='complaint',
            name='case_type',
            field=models.ForeignKey(limit_choices_to={'category': 'Case Type'}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='complaints_as_case_type', to='management.mastersetting'),
        ),
        migrations.AddField(
            model_name='complaint',
            name='channel',
            field=models.ForeignKey(limit_choices_to={'category': 'Channel'}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='complaints_as_channel', to='management.mastersetting'),
        ),
        migrations.AddField(
            model_name='complaint',
            name='country',
            field=models.ForeignKey(limit_choices_to={'category': 'Country'}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='complaints_as_country', to='management.mastersetting'),
        ),
        migrations.AddField(
            model_name='complaint',
            name='material',
            field=models.ForeignKey(limit_choices_to={'category': 'Material'}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='complaints_as_material', to='management.mastersetting'),
        ),
        migrations.AddField(
            model_name='complaint',
            name='person',
            field=models.ForeignKey(limit_choices_to={'category': 'Person'}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='complaints_as_person', to='management.mastersetting'),
        ),
        migrations.AddField(
            model_name='complaint',
            name='series',
            field=models.ForeignKey(limit_choices_to={'category': 'Series'}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='complaints_as_series', to='management.mastersetting'),
        ),
        migrations.CreateModel(
            name='Model',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('brand', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='models', to='management.brand')),
            ],
            options={
                'unique_together': {('brand', 'name')},
            },
        ),
        migrations.AddField(
            model_name='complaint',
            name='model',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='management.model'),
        ),
        migrations.CreateModel(
            name='SubModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('model', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='submodels', to='management.model')),
            ],
            options={
                'unique_together': {('model', 'name')},
            },
        ),
        migrations.AddField(
            model_name='complaint',
            name='sub_model',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='management.submodel'),
        ),
        migrations.CreateModel(
            name='YearRange',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year_start', models.PositiveSmallIntegerField()),
                ('year_end', models.PositiveSmallIntegerField()),
                ('number_of_seats', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('number_of_doors', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('layout_code', models.CharField(max_length=100, unique=True)),
                ('sub_model', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='year_ranges', to='management.submodel')),
            ],
            options={
                'unique_together': {('sub_model', 'year_start', 'year_end')},
            },
        ),
        migrations.AddField(
            model_name='complaint',
            name='year',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='management.yearrange'),
        ),
    ]
