# Generated by Django 3.2.6 on 2021-08-23 13:47

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('main', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('real_name', models.CharField(max_length=20)),
                ('self_intro', models.CharField(blank=True, max_length=140)),
                ('slug', models.SlugField(allow_unicode=True, max_length=100)),
                ('persona_type', models.CharField(choices=[('Adam', '다른 사람들, 특히 내가 관심을 갖고 있는 이들의 생각을 구경하는 것을 즐긴다.'), ('Brian', '나에게 생각할거리가 주어지는 것을 좋아한다.'), ('Claire', '나의 생각을 글이나 메모로 정리하는 데 익숙하다.'), ('Diana', '삶에 동기부여와 자극을 주는 컨텐츠를 종종/자주 찾아본다.'), ('Other', '기타')], max_length=50)),
                ('is_editor', models.BooleanField(default=False)),
                ('saved_answers', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='userinfo', to='main.answersforfromus')),
                ('this_user', models.OneToOneField(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='userinfo', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
