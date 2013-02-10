from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models.signals import post_save
import datetime
import logging

logger = logging.getLogger(__name__)


class Poll(models.Model):
    question = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')

    def was_published_recently(self):
        return self.pub_date >= timezone.now() - datetime.timedelta(days=1)

    was_published_recently.admin_order_field = 'pub_date'
    was_published_recently.boolean = True
    was_published_recently.short_description = 'Published recently?'

    def __unicode__(self):
        return "POLL: " + self.question


class Choice(models.Model):
    poll = models.ForeignKey(Poll)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField()

    def __unicode__(self):
        return "CHOICE: " + self.choice_text


class UserProfile(models.Model):
    #user = models.ForeignKey(User, unique=True)
    user = models.OneToOneField(User)
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
