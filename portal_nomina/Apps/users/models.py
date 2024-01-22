from django.db import models
from django.contrib.auth.models import User
from django.conf import settings



TYPE_BUSINESS = (
    ('S', 'Staff'),
    ('O', 'Operaciones'),
    ('P', 'Payroll'),
    ('L', 'Latin'),
)

ROLES = (
  ('A', 'Admin'),
  ('S', 'Staff'),
  ('B', 'Business'),
  ('E', 'Employee'),
)
class Profile(models.Model):
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, null= True)
    name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    picture = models.ImageField(upload_to="uploads/") # file will be uploaded to MEDIA_ROOT / uploads 
    email = models.EmailField(max_length=254, default =settings.USERNAME_FK)
    role = models.CharField(max_length=1, choices=ROLES)
    
    def __str__(self):
        return '{} {}'.format( self.name, self.role, )
    
    
    