from django.db import models
from django.db.models import signals
from django.contrib.auth.models import User
from .default_logo import DEFAULT_LOGO_BASE64
from .default_image_url import DEFAULT_IMG_FRONT_URL, DEFAULT_IMG_BACK_URL
import base64

# BLACK = 'BK'
# BEIGE = 'BG'
# BLUE = 'BL'
# IVORY = 'IV'
# PINK = 'PK'
# RED = 'RD'
# WHITE = 'WT'
# COLOR_CHOICES = (
#     (BLACK, 'Black'),
#     (BEIGE, 'Beige'),
#     (BLUE, 'Blue'),
#     (IVORY, 'Ivory'),
#     (PINK, 'Pink'),
#     (RED, 'Red'),
#     (WHITE, 'White'),
# )

MAJOR = 'MJ'
CLUB = 'CL'
USER = 'UR'
GROUP_TYPE = (
    (MAJOR, 'Major'),
    (CLUB, 'Club'),
    (USER, 'User'),
)

class Group(models.Model):
    group_type = models.CharField(
        max_length=2,
        choices=GROUP_TYPE,
        default=CLUB,
    )
    group_name = models.CharField(max_length=50)
    users = models.ManyToManyField('auth.User')
    master = models.ManyToManyField('auth.User', related_name="master")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.group_name

class Comment(models.Model):
    name = models.TextField(default="anonymous", blank=True, null=True)
    writer = models.ForeignKey('auth.User', related_name="writer", on_delete=models.CASCADE)
    design = models.ForeignKey('Design', on_delete=models.CASCADE)
    comment = models.TextField(default="Good Job!", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    who_c = models.ManyToManyField('auth.User', related_name="who_c", blank=True)

class Design(models.Model):
    name = models.CharField(max_length=50, blank=True, null=True)
    owner = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    who = models.ManyToManyField('auth.User', related_name="who", blank=True)
    body = models.CharField(
        max_length=7,
        default="#001c58",
    )
    button = models.CharField(
        max_length=7,
        default="#fcfcfc",
    )
    sleeve = models.CharField(
        max_length=7,
        default="#fcfcfc",
    )
    banding = models.CharField(
        max_length=7,
        default="#001c58",
    )
    stripe = models.CharField(
        max_length=7,
        default="#fcfcfc",
    )
    front_chest_text = models.OneToOneField('Text', related_name='front_chest', null=True, blank=True, on_delete=models.SET_NULL)
    right_arm_text = models.OneToOneField('Text', related_name='right_arm', null=True, blank=True, on_delete=models.SET_NULL)
    upper_back_text = models.OneToOneField('Text', related_name='upper_back', null=True, blank=True, on_delete=models.SET_NULL)
    middle_back_text = models.OneToOneField('Text', related_name='middle_back', null=True, blank=True, on_delete=models.SET_NULL)
    lower_back_text = models.OneToOneField('Text', related_name='lower_back', null=True, blank=True, on_delete=models.SET_NULL)
    front_logo = models.OneToOneField('Logo', related_name='front_logo', null=True, blank=True, on_delete=models.SET_NULL)
    back_logo = models.OneToOneField('Logo', related_name='back_logo', null=True, blank=True, on_delete=models.SET_NULL)

    front_image_url = models.TextField(default=DEFAULT_IMG_FRONT_URL, blank=True, null=True)
    back_image_url = models.TextField(default=DEFAULT_IMG_BACK_URL, blank=True, null=True)

    def __str__(self):
        return str(self.group)+'_'+str(self.owner)+"_"+str(self.id)

class Logo(models.Model):
    src = models.TextField(default=DEFAULT_LOGO_BASE64, blank=True, null=True)
    width = models.FloatField(default=571)
    height = models.FloatField(default=589)
    left = models.FloatField(default=0)
    top = models.FloatField(default=0)
    scaleX = models.FloatField(default=1)
    scaleY = models.FloatField(default=1)

class Text(models.Model):
    textvalue = models.CharField(max_length=50)
    fontFamily = models.CharField(max_length=50)
    fill = models.CharField(max_length=50)
    fontStyle = models.CharField(max_length=50)
    fontSize = models.IntegerField(default=100)
    left = models.FloatField(default=0)
    top = models.FloatField(default=0)
    stroke = models.CharField(
        max_length=7,
        default="#fcfcfc",
    )
    strokeWidth = models.IntegerField(default=0)
    scaleX = models.FloatField(default=1)
    scaleY = models.FloatField(default=1)
    width = models.FloatField(default=0)
    height = models.FloatField(default=0)


class Profile(models.Model):
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE,primary_key=True)
    number = models.IntegerField(default=1)
    user_group = models.OneToOneField(
        Group,
        on_delete=models.CASCADE,
        related_name='user_group',
        null=True,
    )
    groups = models.ManyToManyField('Group')
    recent = models.OneToOneField(
        Design,
        null=True,
        on_delete=models.SET_NULL
    )

    def __str__(self):
        return str(self.user)

## 클래스 밖에 정의된 함수입니다 
# def create_profile(sender, instance, created, **kwargs):
#     #create Profile for every new User model
#     if created:
#         Profile.objects.create(user=instance)
# signals.post_save.connect(create_profile, sender='auth.User', weak=False)
##, dispatch_uid='models.create_profile'

def create_profile_and_group(sender, instance, created, **kwargs):
    #create User Group for every new User model
    if created:
        group = Group()
        group.group_type = USER
        group.group_name = 'user_group_'+instance.username
        group.save()
        group.master.add(instance)
        group.users.add(instance)
        group.save()

        profile = Profile()
        profile.user=instance
        profile.user_group=group
        profile.save()
        profile.groups.add(group)
        
signals.post_save.connect(create_profile_and_group, sender='auth.User', weak=False)
