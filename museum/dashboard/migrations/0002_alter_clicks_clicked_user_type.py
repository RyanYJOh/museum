# Generated by Django 3.2.6 on 2021-10-21 22:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='clicks',
            name='clicked_user_type',
            field=models.CharField(choices=[('Adam', 'Adam'), ('Brian', 'Brian'), ('Claire', 'Claire')], max_length=20),
        ),
    ]
