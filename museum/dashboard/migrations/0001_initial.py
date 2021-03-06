# Generated by Django 3.2.6 on 2021-09-20 06:43

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('main', '0020_auto_20210905_0028'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Clicks',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('clicked_from', models.CharField(blank=True, max_length=20, null=True)),
                ('ans_type', models.CharField(choices=[('us', 'us'), ('self', 'self')], max_length=10)),
                ('clicked_at', models.DateField(auto_now_add=True)),
                ('clicked_user_type', models.CharField(choices=[('Adam', 'Adam'), ('Brian', 'Brian'), ('Claire', 'Claire'), ('Diana', 'Diana')], max_length=20)),
                ('ans_self_ref', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='clicks', to='main.answersforfromself')),
                ('ans_us_ref', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='clicks', to='main.answersforfromus')),
                ('clicked_by', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='clicked_by', to=settings.AUTH_USER_MODEL)),
                ('whose_post', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='clicks', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
