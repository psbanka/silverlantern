from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
import logging

logger = logging.getLogger(__name__)


class UserProfile(models.Model):
    #user = models.ForeignKey(User, unique=True)
    user = models.OneToOneField(User)
    code = models.CharField(max_length=200, blank=True, null=True)
    access_token = models.CharField(max_length=200, blank=True, null=True)
    token_expiration = models.DateField(blank=True, null=True)
    token_type = models.CharField(max_length=20, blank=True, null=True)
    id_token = models.CharField(max_length=1000, blank=True, null=True)

    def __unicode__(self):
        return "%s's profile" % self.user


def create_user_profile(sender, instance, created, **kwargs):
    logger.info("in create_user_profile (%s)" % created)
    if created:
        profile, created = UserProfile.objects.get_or_create(user=instance)

post_save.connect(create_user_profile, sender=User)

User.profile = property(lambda u: u.get_profile())
