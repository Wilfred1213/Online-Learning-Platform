from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission

# Create your views here.
class CustomUser(AbstractUser):
    is_instructor= models.BooleanField('Am an instructor', default = False )
    is_student = models.BooleanField('Am a Student', default = False )
    photo = models.ImageField(upload_to='media', null = True)
    
      
    
    class Meta(AbstractUser.Meta):
        # swappable = 'authentications.CustomUser'
    
        app_label = 'authentications'
    
    def __str__(self):
        return self.username
    

# CustomUser.groups.field.remote_field.related_name = 'customuser_set'
# CustomUser.user_permissions.field.remote_field.related_name = 'customuser_permissions_set'
# PersonalUser.groups.field.remote_field.related_name = 'personaluser_set'
# PersonalUser.user_permissions.field.remote_field.related_name = 'personaluser_permissions_set'

