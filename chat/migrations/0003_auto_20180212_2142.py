# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-02-12 21:42
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django_currentuser.middleware


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0002_auto_20180212_2139'),
    ]

    operations = [
        migrations.AlterField(
            model_name='privateroom',
            name='owner',
            field=models.ForeignKey(default=django_currentuser.middleware.get_current_authenticated_user, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
