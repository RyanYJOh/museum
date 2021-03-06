# Generated by Django 3.2.6 on 2021-09-02 13:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('member', '0002_auto_20210826_2126'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userinfo',
            name='profile_image',
            field=models.ImageField(default='profile_images/default_psa', null=True, upload_to='profile_images'),
        ),
        migrations.AlterField(
            model_name='userinfo',
            name='real_name',
            field=models.CharField(blank=True, default='내 이름', max_length=20),
        ),
        migrations.AlterField(
            model_name='userinfo',
            name='self_intro',
            field=models.CharField(blank=True, default='나에 대한 간단한 소개', max_length=140),
        ),
    ]
