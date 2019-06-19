from rest_framework import serializers
from django.contrib.auth.models import User
from homepage.models import *
from django.db.models import Sum, Q
import base64
from django.conf import settings
from rest_framework.fields import (  # NOQA # isort:skip
    CreateOnlyDefault, CurrentUserDefault, SkipField, empty
)

class UserSerializer(serializers.ModelSerializer):
    '''
    def create(self, validated_data):
        profile_data = validated_data.pop('profile', None)
        user = super(UserSerializer, self).create(validated_data)
        self.update_or_create_profile(user, profile_data)
        return user
    '''
    def update(self, instance, validated_data):
        instance.set_password(validated_data['password'])
        instance.save()
        return instance
    '''
    def update_or_create_profile(self, user, profile_data):
        Profile.objects.update_or_create(user=user, defaults=profile_data)
    '''
    class Meta:
        model = User
        #article
        fields = ('id','username','password')



# class ProfileSerializer(serializers.ModelSerializer):
#     user= serializers.ReadOnlyField(source='user.username')
#     domain = serializers.SerializerMethodField()
#     def get_domain(self, obj):
#         return 'http://'+self.context['domain']+obj.myimage.url
#     class Meta:
#         model = Profile
#         fields = ('user','myname','mybelong','myintro', 'myimage', 'domain')
class ProfileSerializer(serializers.ModelSerializer):
    user= serializers.ReadOnlyField(source='user.username')
    class Meta:
        model = Profile
        fields = ('user','recent','user_group')

class GroupSerializer(serializers.ModelSerializer):
    admin = serializers.SerializerMethodField()
    member = serializers.SerializerMethodField()
    
    def __init__(self, instance=None, user=None, data=empty, **kwargs):
        self.instance = instance
        if data is not empty:
            self.initial_data = data
        self.partial = kwargs.pop('partial', False)
        self._context = kwargs.pop('context', {})
        self.user = user
        kwargs.pop('many', None)
        super().__init__(**kwargs)

    def get_admin(self, obj):
        if self.user == None:
            return False
        else:
            return self.user in obj.master.all()

    def get_member(self, obj):
        if self.user == None:
            return False
        else:
            return self.user in obj.users.all()
    
    class Meta:
        model = Group
        fields = '__all__'

class TextSerializer(serializers.ModelSerializer):
    class Meta:
        model = Text
        fields = '__all__'

class LogoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Logo
        fields = '__all__'

class DesignDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Design
        fields = ('body', 'button', 'sleeve', 'banding', 'stripe')

class DesignTextSerializer(serializers.ModelSerializer):
    frontchest = serializers.SerializerMethodField()
    rightarm = serializers.SerializerMethodField()
    upperback = serializers.SerializerMethodField()
    middleback = serializers.SerializerMethodField()
    lowerback = serializers.SerializerMethodField()

    def get_frontchest(self, obj):
        if obj.front_chest_text == None:
            return None
        return TextSerializer(obj.front_chest_text).data
    
    def get_rightarm(self, obj):
        if obj.right_arm_text == None:
            return None
        return TextSerializer(obj.right_arm_text).data
    
    def get_upperback(self, obj):
        if obj.upper_back_text == None:
            return None
        return TextSerializer(obj.upper_back_text).data
    
    def get_middleback(self, obj):
        if obj.middle_back_text == None:
            return None
        return TextSerializer(obj.middle_back_text).data
    
    def get_lowerback(self, obj):
        if obj.lower_back_text == None:
            return None
        return TextSerializer(obj.lower_back_text).data

    class Meta:
        model = Design
        fields = ('frontchest', 'rightarm', 'upperback', 'middleback', 'lowerback')

class DesignLogoSerializer(serializers.ModelSerializer):
    front = serializers.SerializerMethodField()
    back = serializers.SerializerMethodField()

    def get_front(self, obj):
        if obj.front_logo == None:
            return None
        return LogoSerializer(obj.front_logo).data

    def get_back(self, obj):
        if obj.back_logo == None:
            return None
        return LogoSerializer(obj.back_logo).data

    class Meta:
        model = Design
        fields = ('front', 'back')

class DesignImageSerializer(serializers.ModelSerializer):
    frontImg = serializers.SerializerMethodField()
    backImg = serializers.SerializerMethodField()

    def get_frontImg(self, obj):
        return obj.front_image_url

    def get_backImg(self, obj):
        return obj.back_image_url

    class Meta:
        model = Design
        fields = ('frontImg', 'backImg')

class UserDesignSerializer(serializers.ModelSerializer):    
    design = serializers.SerializerMethodField()
    text = serializers.SerializerMethodField()
    logo = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    def get_design(self, obj):
        return DesignDetailSerializer(obj).data
    def get_text(self, obj):
        return DesignTextSerializer(obj).data
    def get_logo(self, obj):
        return DesignLogoSerializer(obj).data
    def get_image(self, obj):
        return DesignImageSerializer(obj).data

    class Meta:
        model = Design
        fields = ('name', 'id', 'group', 'design', 'text', 'logo', 'image')

class CommentSerializer(serializers.ModelSerializer):
    auth = serializers.SerializerMethodField()
    likes = serializers.SerializerMethodField()
    liked = serializers.SerializerMethodField()

    def __init__(self, instance=None, user=None, data=empty, **kwargs):
        self.instance = instance
        if data is not empty:
            self.initial_data = data
        self.partial = kwargs.pop('partial', False)
        self._context = kwargs.pop('context', {})
        self.user = user
        kwargs.pop('many', None)
        super().__init__(**kwargs)

    def get_auth(self, obj):
        if self.user == None:
            return False
        else:
            return self.user in obj.design.group.master.all() or self.user == obj.writer

    def get_likes(self, obj):
        return obj.who_c.all().count()
    
    def get_liked(self, obj):
        return self.user in obj.who_c.all()

    class Meta:
        model = Comment
        fields = ('id', 'design', 'name', 'auth', 'likes', 'liked', 'writer', 'created_at', 'comment')

class GroupDesignSerializer(serializers.ModelSerializer):
    auth = serializers.SerializerMethodField()
    likes = serializers.SerializerMethodField()
    liked = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()

    def __init__(self, instance=None, user=None, data=empty, **kwargs):
        self.instance = instance
        if data is not empty:
            self.initial_data = data
        self.partial = kwargs.pop('partial', False)
        self._context = kwargs.pop('context', {})
        self.user = user
        kwargs.pop('many', None)
        super().__init__(**kwargs)

    def get_auth(self, obj):
        if self.user == None:
            return False
        else:
            return self.user in obj.group.master.all() or self.user == obj.owner

    def get_likes(self, obj):
        return obj.who.all().count()

    def get_liked(self, obj):
        return self.user in obj.who.all()

    def get_comments(self, obj):
        c_set = Comment.objects.all().filter(design=obj).order_by('created_at').reverse()
        return CommentSerializer(c_set, user=self.user, many=True).data
    
    class Meta:
        model = Design
        fields = '__all__'

class MemberSerializer(serializers.ModelSerializer):
    admin = serializers.SerializerMethodField()
    
    def __init__(self, instance=None, group=None, data=empty, **kwargs):
        self.instance = instance
        if data is not empty:
            self.initial_data = data
        self.partial = kwargs.pop('partial', False)
        self._context = kwargs.pop('context', {})
        self.group = group
        kwargs.pop('many', None)
        super().__init__(**kwargs)

    def get_admin(self, obj):
        if self.group == None:
            return False
        else:
            return obj in self.group.master.all()
            
    class Meta:
        model = User
        fields = ('id','username','admin')
