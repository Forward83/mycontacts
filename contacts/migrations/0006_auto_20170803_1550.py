# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-08-03 12:50
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contacts', '0005_contact_media_url_list'),
    ]

    operations = [
        migrations.CreateModel(
            name='ContactPhoto',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('photo', models.ImageField(blank=True, null=True, upload_to='<django.db.models.query_utils.DeferredAttribute object at 0x000001FCE71E7198>/photos')),
                ('thumbnail', models.ImageField(blank=True, editable=False, null=True, upload_to='<django.db.models.query_utils.DeferredAttribute object at 0x000001FCE71E7198>/thumbs')),
            ],
        ),
        migrations.RemoveField(
            model_name='contact',
            name='photo',
        ),
        migrations.RemoveField(
            model_name='contact',
            name='thumbnail',
        ),
        migrations.AddField(
            model_name='contactphoto',
            name='contact',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contacts.Contact'),
        ),
    ]
