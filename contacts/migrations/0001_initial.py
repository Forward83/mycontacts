# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-02-04 12:00
from __future__ import unicode_literals

import contacts.models
from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('firstname', models.CharField(max_length=30)),
                ('lastname', models.CharField(blank=True, max_length=40, null=True)),
                ('secondname', models.CharField(blank=True, max_length=30, null=True)),
                ('mobile', models.CharField(max_length=15, validators=[django.core.validators.RegexValidator(code='invalid_mobile', message="Phone number must be entered in the format: '+380(67)9999999'. Up to 15 digits allowed.", regex='^\\+380\\([0-9]{2}\\)[0-9]{7}$')])),
                ('personal_phone', models.CharField(blank=True, max_length=15, null=True)),
                ('business_phone', models.CharField(blank=True, max_length=4, null=True)),
                ('company', models.CharField(blank=True, max_length=15, null=True)),
                ('position', models.TextField(blank=True, null=True)),
                ('address', models.TextField(blank=True, null=True)),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('star', models.BooleanField(default=False)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ContactPhoto',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('photo', models.ImageField(blank=True, null=True, upload_to=contacts.models.user_directory_path)),
                ('thumbnail', models.ImageField(blank=True, editable=False, null=True, upload_to=contacts.models.user_directory_path)),
                ('load_date', models.DateTimeField(auto_now_add=True)),
                ('active', models.BooleanField(default=False)),
                ('contact', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contacts.Contact')),
            ],
            options={
                'ordering': ['-load_date'],
            },
        ),
        migrations.CreateModel(
            name='Dublicate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('count', models.SmallIntegerField()),
                ('contact_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contacts.Contact')),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(blank=True, max_length=20)),
                ('last_name', models.CharField(blank=True, max_length=20)),
                ('email', models.EmailField(blank=True, max_length=254)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
