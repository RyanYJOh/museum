# Generated by Django 3.2.6 on 2021-10-31 17:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('member', '0004_alter_userinfo_profile_image'),
        ('ndaychallenge', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='challenge',
            name='co_host',
            field=models.ManyToManyField(blank=True, related_name='cohosts', to='member.UserInfo'),
        ),
        migrations.AddField(
            model_name='challenge',
            name='host',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='host', to='member.userinfo'),
        ),
        migrations.AlterField(
            model_name='challenge',
            name='desc',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='challenge',
            name='participant',
            field=models.ManyToManyField(blank=True, related_name='participant', to='member.UserInfo'),
        ),
        migrations.AlterField(
            model_name='challenge',
            name='passed',
            field=models.ManyToManyField(blank=True, related_name='passed', to='member.UserInfo'),
        ),
    ]
