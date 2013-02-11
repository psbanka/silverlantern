from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
import logging
import django.utils.timezone

logger = logging.getLogger(__name__)


class WordUse(models.Model):
    user = models.ForeignKey(User)
    word = models.CharField(max_length=100, primary_key=True)
    times_used = models.IntegerField()
    last_time_used = models.DateTimeField()
    last_sent_to = models.CharField(max_length=100)

    def __unicode__(self):
        return "%s used %d times." % (self.word, self.times_used)


class UserProfile(models.Model):
    #user = models.ForeignKey(User, unique=True)
    user = models.OneToOneField(User)
    code = models.CharField(max_length=200, blank=True, null=True)
    access_token = models.CharField(max_length=200, blank=True, null=True)
    token_expiration = models.DateTimeField(blank=True, null=True)
    token_type = models.CharField(max_length=20, blank=True, null=True)
    id_token = models.CharField(max_length=1000, blank=True, null=True)
    last_message_processed = models.IntegerField(blank=True, null=True)

    def token_is_current(self):
        token_expiration = self.token_expiration
        if token_expiration:
            if token_expiration > django.utils.timezone.now():
                return True
        return False

    def __unicode__(self):
        return "%s's profile" % self.user


def create_user_profile(sender, instance, created, **kwargs):
    logger.info("in create_user_profile (%s)" % created)
    if created:
        profile, created = UserProfile.objects.get_or_create(user=instance)

post_save.connect(create_user_profile, sender=User)

User.profile = property(lambda u: u.get_profile())
