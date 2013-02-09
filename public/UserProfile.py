from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.db import models


class UserProfile(models.Model):
    user = models.OneToOneField(User)
    access_token = models.CharField(max_length=200)
    token_expiration = models.DateField()
    token_type = models.Charfield(max_length=20)
    id_token = models.Charfield(max_length=1000)

    def __str__(self):
        return "%s's profile" % self.user


def create_user_profile(sender, instance, created, **kwargs):
    if created:
        profile, created = UserProfile.objects.get_or_create(user=instance)

post_save.connect(create_user_profile, sender=User)

User.profile = property(lambda u: u.get_profile())
