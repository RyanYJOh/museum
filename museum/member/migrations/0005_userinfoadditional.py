# Generated by Django 3.2.6 on 2022-01-01 16:51

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('member', '0004_alter_userinfo_profile_image'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserInfoAdditional',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('best_book', models.CharField(blank=True, default='📚', max_length=100)),
                ('thoughts', models.CharField(blank=True, default='💬', max_length=100)),
                ('enthusiasm', models.CharField(blank=True, default='🔥', max_length=100)),
                ('this_user', models.OneToOneField(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='userinfoadditional', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]