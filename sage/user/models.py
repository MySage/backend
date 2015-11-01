from django.db import models


class User(models.Model):
    name = models.CharField(max_length=200)
    username = models.CharField(max_length=200, unique=True)
    password = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=20)

    def __str__(self):
        return self.name + ":" + self.phone_number
