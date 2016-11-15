from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

CHARFIELD_MAX = 4000

class Profile(models.Model):
    """ Author. """
    user = models.OneToOneField(User)
    nick = models.CharField(max_length=80)

    def __str__(self):
        return self.nick

class Chatroom(models.Model):
    """ Chatroom. """
    title = models.CharField(max_length=80)
    description = models.CharField(max_length=300)
    # Password is optional. Blank means no password.
    password = models.CharField(max_length=CHARFIELD_MAX, blank=True)
    creator = models.ForeignKey(Profile)

    def __str__(self):
        return self.title

class Post(models.Model):
    """ Message. """
    content = models.CharField(max_length=CHARFIELD_MAX)
    publish_date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(Profile)
    chatroom = models.ForeignKey(Chatroom)

    def __str__(self):
        return self.content

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """ Create Profile model when user is created. """
    if created:
        Profile.objects.create(user=instance, nick=instance.username)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """ Save Profile model when user is saved. """
    instance.profile.save()
