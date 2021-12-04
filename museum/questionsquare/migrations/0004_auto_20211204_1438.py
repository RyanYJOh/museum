# Generated by Django 3.2.6 on 2021-12-04 14:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('member', '0004_alter_userinfo_profile_image'),
        ('questionsquare', '0003_auto_20211204_1438'),
    ]

    operations = [
        migrations.AlterField(
            model_name='answersforfromothers',
            name='author',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='answersforfromothers', to='member.userinfo'),
        ),
        migrations.AlterField(
            model_name='questionsfromothers',
            name='questioner',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='questionfromothers', to='member.userinfo'),
        ),
    ]
