# Generated by Django 3.2.6 on 2021-09-04 15:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0018_auto_20210905_0011'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='answersforfromself',
            name='answer_no',
        ),
        migrations.RemoveField(
            model_name='answersforfromus',
            name='answer_no',
        ),
    ]
