from django.db import models
from django.conf import settings

# Create your models here.
class Task(models.Model):
    Complete = models.BooleanField(default=False)
    Todo = models.CharField(max_length=100)
    Related = models.ManyToManyField(settings.AUTH_USER_MODEL)

position = [('M','Manager'),('S','Supervisor'),('G','General Staff')]

class Employee(models.Model):
    Name = models.CharField(max_length=20)
    Contact = models.CharField(max_length=45)
    ProfilePhoto = models.ImageField(default="employee/default.png",upload_to='employee')
    Active = models.BooleanField(default=True)
    Position = models.CharField(max_length=1,choices=position)