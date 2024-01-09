from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager, PermissionsMixin)
from django.db import models
from django.utils import timezone

from django.conf import settings
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.hashers import check_password


#User=get_user_model()



ROLES = (
  ('A', 'Admin'),
  ('S', 'Staff'),
  ('B', 'Business'),
  ('E', 'Employee'),
)

TYPE_BUSINESS = (
    ('S', 'Staff'),
    ('O', 'Operaciones'),
    ('P', 'Payroll'),
    ('L', 'Latin'),
)



class UserManager(BaseUserManager):
    def _create_user(self, email, password, is_staff, is_superuser, role = 'P'):
        if not email:
            raise ValueError("Please, enter your e-mail")
      
        if not password:
            raise ValueError("PASSWORD?!?!?!? HELLO??")
        
        user = self.model(
             email = self.normalize_email(email))
    
        user.set_password(password)
        user.save()
        return user
    
    def create_user(self, email, password=None):
        
        return self._create_user(email, password, False, False)
    
    def create_superuser(self, email, password):
        
        user = self._create_user(email, password)
        user.is_staff()
        user.is_superuser = True
        user.role = 'S'
        user.save()
        return user

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    role = models.CharField(choices=ROLES, default='P', max_length=1)
    objects = UserManager()
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    objects = UserManager()
    is_superuser = models.BooleanField(default = False)
    type_business =  models.CharField(choices = TYPE_BUSINESS, null = True, max_length =1)
    
    
    USERNAME_FIELD = "email"

    
    def __str__(self):
        return "@{}".format(self.email)
    
    def get_short_name(self):
        return self.email
    def get_long_name(self):
        return "@{}".format(self.email)
