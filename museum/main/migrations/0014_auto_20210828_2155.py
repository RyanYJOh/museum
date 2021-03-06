# Generated by Django 3.2.6 on 2021-08-28 12:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0013_auto_20210828_1659'),
    ]

    operations = [
        migrations.CreateModel(
            name='savedAnswers',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ans_type', models.CharField(choices=[('us', 'us'), ('self', 'self')], max_length=10)),
                ('ans_no', models.IntegerField()),
            ],
        ),
        migrations.AddField(
            model_name='answersforfromself',
            name='answer_no',
            field=models.IntegerField(null=True, unique=True),
        ),
        migrations.AddField(
            model_name='answersforfromself',
            name='type',
            field=models.CharField(blank=True, default='self', max_length=10),
        ),
        migrations.AddField(
            model_name='answersforfromus',
            name='answer_no',
            field=models.IntegerField(null=True, unique=True),
        ),
        migrations.AddField(
            model_name='answersforfromus',
            name='type',
            field=models.CharField(blank=True, default='us', max_length=10),
        ),
        migrations.AddField(
            model_name='questionsfromself',
            name='question_no',
            field=models.IntegerField(null=True, unique=True),
        ),
    ]
