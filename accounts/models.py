from django.db import models
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager,PermissionsMixin

# Create your models here.
class UserManager(BaseUserManager):
    def create_user(self, username, email, password):
        if username is None:
            raise TypeError("Username is required")
        if email is None:
            raise TypeError("Email field is required")
        user = self.model(username = username, email = self.normalize_email(email))
        user.set_password(password)
        user.save()
        return user
    
    # create a super user
    def create_superuser(self, username, email, password):
        if password is None:
            raise TypeError("Superusers must have password")
        user = self.create_user(username, email, password)
        user.is_superuser = True
        user.is_staff = True
        user.save()
        return user
        
        
class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=50)
    email = models.EmailField(max_length=100, unique = True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    objects = UserManager()
    
    def __str__(self):
        return self.username