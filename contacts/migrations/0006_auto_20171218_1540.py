# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-12-18 13:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contacts', '0005_auto_20171218_1108'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contact',
            name='secondname',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
    ]
