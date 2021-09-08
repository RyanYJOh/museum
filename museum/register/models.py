from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, AbstractUser
# Create your models here.

# class CustomUser(AbstractUser):
#     USERNAME_FIELD = 'email'

#     def natural_key(self):
#         return dict(email=self.email)

# CustomUser._meta.get_field('email')._unique = True
# CustomUser._meta.get_field('email')._blank = False
# CustomUser._meta.get_field('username')._unique = False
# CustomUser._meta.get_field('username')._blank = True
# CustomUser._meta.get_field('username')._null = True

class UserManager(BaseUserManager):
    """User 에서 사용하기 위한 UserManager 생성"""
    def create_user(self, email, password=None, **extra_fields):
        """일반 유저로 생성할 경우"""
        if not email:
            raise ValueError('이메일을 입력해주세요')

        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        """superuser 로 user 를 생성할 경우 필드값을 True 로 변경"""
        user = self.create_user(email, password)
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """UserManager 를 objects 필드에 사용"""

    email = models.EmailField(max_length=255, unique=True)

    # UserManager 을 재정의하여 사용
    objects = UserManager()
    # USERNAME 를 email 로 사용
    USERNAME_FIELD = 'email'