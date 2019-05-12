from django.shortcuts import render
from django.core.files import File
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import HttpResponseRedirect,HttpResponse
from django.views.decorators.csrf import csrf_exempt
from homepage.models import *
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .forms import DesignForm, GroupForm
from .serializers import *
from .permissions import *

from base64 import b64decode as decode
import json
import re
# Create your views here.


class AuthList(APIView):
    permission_classes = (IsAuthenticated,)
    def get(self, request, format=None):
        content = {
            'status': 'user is authenticated'
        }
        return Response(content)

@api_view(['GET', 'POST','DELETE'])
@permission_classes((IsAuthenticatedOrPOSTOnly,))
def user_list(request):
    if request.method == 'GET':
        serializer = UserSerializer(User.objects.all(), many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        # requested data should contain username, password attributes.
        auth = request.data
        try: # if request is bad request, return 400
            username = auth['username']
            pwd = auth['password']
            if len(username)<4 or len(username)>20:
                return Response(status = status.HTTP_400_BAD_REQUEST)
            p = re.compile('\W+')
            if (p.search(username) != None or pwd == ''):
                return Response(status = status.HTTP_400_BAD_REQUEST)
        except KeyError:
            return Response(status = status.HTTP_400_BAD_REQUEST)
        try: # if there is an user that has same username, return 405
            old_user = User.objects.get(username=username)
            return Response(status = status.HTTP_405_METHOD_NOT_ALLOWED)
        except User.DoesNotExist:
            pass
        user = User.objects.create_user(username, password=pwd)
        user.save()
        return Response(status = status.HTTP_201_CREATED)
    elif request.method == 'DELETE':
        # requested data should contain username attribute.
        request.user.delete()
        return Response(status = status.HTTP_204_NO_CONTENT)

@api_view(['GET','PUT','DELETE'])
def user_detail(request, username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if request.user.id == None:
        return Response(status=status.HTTP_403_FORBIDDEN)
    if request.method == 'GET':
        serializer = UserSerializer(user)
        return Response(serializer.data)
    elif request.method == 'PUT':
        if user!=request.user:
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        serializer = UserSerializer(user,data=request.data)
        if serializer.is_valid():
            # if password is bad, return 400
            pwd=request.data['password']
            if(pwd==''):
                return Response(status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            return Response(serializer.data)
        return Response(status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        if user == request.user:
            user.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_403_FORBIDDEN)



@api_view(['GET'])
def profile_list(request):
    if request.user.id==None:
        return Response(status=status.HTTP_403_FORBIDDEN)
    serializer = ProfileSerializer(Profile.objects.all(), many=True)
    if request.method == 'GET':
        return Response(serializer.data)

@api_view(['GET','PUT'])
def profile(request, username):
    context = {'domain': request.META['HTTP_HOST']}
    if request.user.id == None:
        return Response(status= status.HTTP_403_FORBIDDEN)
    try:
        user= User.objects.get(username=username)
        profile=Profile.objects.get(user=user)
    except Profile.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    except User.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if request.method == 'GET':
        serializer=ProfileSerializer(profile, context=context)
        return Response(serializer.data)
    if request.method == 'PUT':
        if profile.user!= request.user:
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        data = request.data
        if 'myimage' in data and data['myimage'] == 'null':
            data['myimage'] = File(open('media/default/defaultImage.jpg', 'rb'))
        serializer = ProfileSerializer(profile, data=data, context=context)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(status=status.HTTP_400_BAD_REQUEST)
    return Response(status=status.HTTP_403_FORBIDDEN)

@api_view(['GET', 'POST', 'PUT', 'DELETE'])
@permission_classes((IsAuthenticatedOrGETOnly,))
def main(request):    
    if request.method == 'GET':
        if request.user.id == None: 
            design = Design()
        else:
            try:
                user = Profile.objects.get(user=request.user)
            except Profile.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)    

            design = user.recent
            if design == None:
                design = Design()
                design.owner = request.user
                design.group = user.user_group
                design.save()
                user.recent = design
        design_serializer = UserDesignSerializer(design)
        return Response(design_serializer.data)
    if request.method == 'POST':
        try:
            design = Design.objects.get(id=1)
        except Design.DoesNotExist:
            design = Design()
        design_serializer = UserDesignSerializer(design)
        return Response(design_serializer.data)
    # elif request.method == 'PUT':
    #     if user!=request.user:
    #         return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
    #     serializer = UserSerializer(user,data=request.data)
    #     if serializer.is_valid():
    #         # if password is bad, return 400
    #         pwd=request.data['password']
    #         if(pwd==''):
    #             return Response(status=status.HTTP_400_BAD_REQUEST)
    #         serializer.save()
    #         return Response(serializer.data)
    #     return Response(status=status.HTTP_400_BAD_REQUEST)
    # elif request.method == 'DELETE':
    #     if user == request.user:
    #         user.delete()
    #         return Response(status=status.HTTP_204_NO_CONTENT)
    #     return Response(status=status.HTTP_403_FORBIDDEN)

@api_view(['GET'])
@permission_classes((IsAuthenticatedOrNothing,))
def group_detail(request, group_id):
    if request.method == 'GET':
        if request.user.id == None:
            return Response(status=status.HTTP_403_FORBIDDEN)
        try:
            user = User.objects.get(username=request.user)
        except User.DoesNotExist:
            return Response(status=status.HTTP_403_FORBIDDEN)
        
        try:
            group = Group.objects.get(id=group_id)
        except Group.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if user not in group.users.all():
            return Response(status=status.HTTP_403_FORBIDDEN)
        
        try:
            designs = Design.objects.all().filter(group=group).order_by('likes').reverse()
        except Design.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        design_serializer = GroupDesignSerializer(designs, many=True)
        
        return Response(design_serializer.data)

@csrf_exempt
@api_view(['POST'])
@permission_classes((IsAuthenticatedOrGETOnly,))
def create_group(request):
    # if request.method == 'GET':
    #     try:
    #         groups = Group.objects.all()
    #     except Group.DoesNotExist:
    #         return Response(status=status.HTTP_404_NOT_FOUND)
    #     group_serializer = GroupSerializer(groups, many=True)
    #     context = {
    #         'form': GroupForm(),
    #         'groupList': group_serializer.data
    #     }
    #     return render(request, 'main/create_group.html', context)

    if request.method == 'POST':
        if request.user.id == None:
            return Response(status=status.HTTP_403_FORBIDDEN)
        try:
            user = User.objects.get(username=request.user)
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        data = json.loads(request.body.decode("utf-8"))
        
        try: # if there is a group that has same groupname, return 409
            old_group = Group.objects.get(group_name = data['groupname'])
            return Response(status = status.HTTP_409_CONFLICT)
        except Group.DoesNotExist:
            pass
        
        group = Group()
        group.group_type = data['grouptype']
        group.group_name = data['groupname']
        group.save()
        group.users.add(user)
        group.master.add(user)
        group_serializer = GroupSerializer(group)
        return Response(group_serializer.data)

@api_view(['GET'])
@permission_classes((IsAuthenticatedOrNothing,))
def group_list(request, username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if request.user.id == None:
        return Response(status=status.HTTP_403_FORBIDDEN)
    if request.method == 'GET':
        try:
            groups = Group.objects.filter(users__username=username)
        except Group.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        group_serializer = GroupSerializer(instance=groups, user=user, many=True)
        return Response(group_serializer.data)  

@api_view(['GET'])
@permission_classes((IsAuthenticatedOrNothing,))
def join_group(request, group_id):
    if request.method == 'GET':
        try:
            group = Group.objects.get(id=group_id)
        except Group.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        if request.user.id == None:
            return Response(status=status.HTTP_403_FORBIDDEN)
        try:
            user = User.objects.get(username=request.user)
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        group.users.add(user)
        group_serializer = GroupSerializer(group)
        return Response(group_serializer.data)

@api_view(['GET'])
def group_list_all(request):
    if request.method == 'GET':
        try:
            groups = Group.objects.all().exclude(group_type='UR').order_by('created_at').reverse()
        except Group.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        group_serializer = GroupSerializer(instance=groups, user=request.user, many=True)
        return Response(group_serializer.data)

@csrf_exempt
@api_view(['GET', 'POST'])
@permission_classes((IsAuthenticatedOrGETOnly,))
def update_likes(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode("utf-8"))
        try:
            design = Design.objects.get(id=data['design_id'])
        except Design.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        design.likes = design.likes + 1
        design.save()

@api_view(['GET'])
@permission_classes((IsAuthenticatedOrNothing,))
def design_list(request, group_id):
    if request.method == 'GET':
        try:
            designs = Design.objects.filter(group__id=group_id)
        except Design.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        design_serializer = GroupDesignSerializer(designs, many=True)
        return Response(design_serializer.data)  