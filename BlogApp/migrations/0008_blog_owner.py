# Generated by Django 5.2.3 on 2025-06-17 19:09

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('BlogApp', '0007_alter_userprofile_contact'),
    ]

    operations = [
        migrations.AddField(
            model_name='blog',
            name='owner',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='blogs', to='BlogApp.logintable'),
        ),
    ]