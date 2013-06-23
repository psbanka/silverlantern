from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
import logging
import django.utils.timezone

logger = logging.getLogger(__name__)
WORD_CATEGORIES = ["hipster", "brianiac", "charming", "whimsical", "romantic"]


class InterestingEmail(models.Model):
    """
    When our system chokes on an email, keep track of it so we
    can figure out how to make the system more resilient.
    """
    text = models.TextField()


class Word(models.Model):
    """
    Our basic word database. We keep track of all our English words here
    """
    word = models.CharField(max_length=100, unique=True)

    def __unicode__(self):
        return "%s" % (self.word)


class Category(models.Model):
    """
    possible
    here, as well possibly, as other interesting features.
    """
    category = models.CharField(max_length=100, unique=True)
    def __unicode__(self):
        return "%s" % self.category


class InterestingWord(models.Model):
    """
    Our database of all words that are fun to learn
    """
    word = models.ForeignKey(Word)
    category = models.ForeignKey(Category)
    info = models.CharField(max_length=1000)

    def __unicode__(self):
        info_snippet = self.info if len(self.info) < 5 else self.info[:5]
        return "IW: %s/%s/%s" % (self.word, self.category, info_snippet)


class WordUse(models.Model):
    """
    Keeps track of the words that the user has already used
    in their writing
    """
    user = models.ForeignKey(User)
    #word = models.CharField(max_length=100, primary_key=True)
    word = models.ForeignKey(Word)
    times_used = models.IntegerField()
    last_time_used = models.DateTimeField()
    last_sent_to = models.CharField(max_length=100)

    def __unicode__(self):
        return "%s (%d)" % (self.word, self.times_used)


class WordsToLearn(models.Model):
    """
    Keeps track of the words that a person wants to learn to use
    """
    user = models.ForeignKey(User)
    #word = models.CharField(max_length=100, primary_key=True)
    word = models.ForeignKey(Word)
    date_added = models.DateTimeField()
    date_completed = models.DateTimeField(blank=True, null=True)


class UserProfile(models.Model):
    """
    Keeps track of extra information about the user, specifically
    credentials for logging into other cloud services.
    """
    #user = models.ForeignKey(User, unique=True)
    user = models.OneToOneField(User)
    code = models.CharField(max_length=200, blank=True, null=True)
    access_token = models.CharField(max_length=200, blank=True, null=True)
    token_expiration = models.DateTimeField(blank=True, null=True)
    token_type = models.CharField(max_length=20, blank=True, null=True)
    id_token = models.CharField(max_length=1000, blank=True, null=True)
    last_message_processed = models.IntegerField(blank=True, null=True)
    last_message_on_server = models.IntegerField(blank=True, null=True)

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
