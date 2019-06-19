from django.shortcuts import render
from django.core.files import File
from django.contrib.auth.models import User
from django.db.models import Q, Count
from django.http import HttpResponseRedirect,HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import JSONParser
# from .forms import DesignForm, GroupForm
from .models import *
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

def set_default_text_and_logo(design, logged_in):
    if design.front_chest_text == None:
        frontchest = Text()
        frontchest.textvalue = "S"
        frontchest.fontFamily = "arial"
        frontchest.fill = "#3f51b5"
        frontchest.fontStyle = "bold"
        frontchest.fontSize = 50
        frontchest.left = 250
        frontchest.top = 110
        frontchest.width = 33.349609375
        frontchest.height = 56.5
        frontchest.stroke = "#000000"
        frontchest.strokeWidth = 2
        if logged_in:
            frontchest.save()
        design.front_chest_text = frontchest
    
    if design.right_arm_text == None:
        rightarm = Text()
        rightarm.textvalue = "19"
        rightarm.fontFamily = "arial"
        rightarm.fill = "#607d8b"
        rightarm.fontStyle = "bold"
        rightarm.fontSize = 50
        rightarm.left = 46
        rightarm.top = 124
        rightarm.width = 55.615234375
        rightarm.height = 56.5
        rightarm.stroke = ""
        rightarm.strokeWidth = 0
        if logged_in:
            rightarm.save()
        design.right_arm_text = rightarm

    if design.upper_back_text == None:
        upperback = Text()
        upperback.textvalue = "SEOUL NAT'L"
        upperback.fontFamily = "arial"
        upperback.fill = "#ffc107"
        upperback.fontStyle = "bold"
        upperback.fontSize = 25
        upperback.left = 135
        upperback.top = 125
        upperback.width = 163.80615234375
        upperback.height = 28.25
        upperback.stroke = ""
        upperback.strokeWidth = 0
        if logged_in:
            upperback.save()
        design.upper_back_text = upperback

    if design.middle_back_text == None:
        middleback = Text()
        middleback.textvalue = "UNIVERSITY"
        middleback.fontFamily = "arial"
        middleback.fill = "#ffc107"
        middleback.fontStyle = "bold"
        middleback.fontSize = 20
        middleback.left = 155
        middleback.top = 155
        middleback.height = 120.01953125
        middleback.width = 22.599999999999998
        middleback.stroke = ""
        middleback.strokeWidth = 0
        if logged_in:
            middleback.save()
        design.middle_back_text = middleback

    if design.lower_back_text == None:
        lowerback = Text()
        lowerback.textvalue = "Department of\nComputer Science"
        lowerback.fontFamily = "arial"
        lowerback.fill = "#ffc107"
        lowerback.fontStyle = "italic"
        lowerback.fontSize = 15
        lowerback.left = 151
        lowerback.top = 256
        lowerback.width = 131.7041015625
        lowerback.height = 36.611999999999995
        lowerback.stroke = ""
        lowerback.strokeWidth = 0
        if logged_in:
            lowerback.save()
        design.lower_back_text = lowerback

    if design.front_logo == None:
        frontlogo = Logo()
        frontlogo.left = 357
        frontlogo.top = 152
        if logged_in:
            frontlogo.save()
        design.front_logo = frontlogo

    if design.back_logo == None:
        backlogo = Logo()
        backlogo.left = 212
        backlogo.top = 216
        if logged_in:
            backlogo.save()
        design.back_logo = backlogo
    
    if logged_in:
        design.save()

def update_text_and_logo(text, logo, design):
    if design.front_chest_text != None:
        design.front_chest_text.delete()
    frontchest = Text()
    frontchest.textvalue = text['frontchest']['textvalue']
    frontchest.fontFamily = text['frontchest']['fontFamily']
    frontchest.fill = text['frontchest']['fill']
    frontchest.fontStyle = text['frontchest']['fontStyle']
    frontchest.fontSize = text['frontchest']['fontSize']
    frontchest.left = text['frontchest']['left']
    frontchest.top = text['frontchest']['top']
    frontchest.stroke = text['frontchest']['stroke']
    frontchest.strokeWidth = text['frontchest']['strokeWidth']
    frontchest.save()
    design.front_chest_text = frontchest
    
    if design.right_arm_text != None:
        design.right_arm_text.delete()
    rightarm = Text()
    rightarm.textvalue = text['rightarm']['textvalue']
    rightarm.fontFamily = text['rightarm']['fontFamily']
    rightarm.fill = text['rightarm']['fill']
    rightarm.fontStyle = text['rightarm']['fontStyle']
    rightarm.fontSize = text['rightarm']['fontSize']
    rightarm.left = text['rightarm']['left']
    rightarm.top = text['rightarm']['top']
    rightarm.stroke = text['rightarm']['stroke']
    rightarm.strokeWidth = text['rightarm']['strokeWidth']
    rightarm.save()
    design.right_arm_text = rightarm

    if design.upper_back_text != None:
        design.upper_back_text.delete()
    upperback = Text()
    upperback.textvalue = text['upperback']['textvalue']
    upperback.fontFamily = text['upperback']['fontFamily']
    upperback.fill = text['upperback']['fill']
    upperback.fontStyle = text['upperback']['fontStyle']
    upperback.fontSize = text['upperback']['fontSize']
    upperback.left = text['upperback']['left']
    upperback.top = text['upperback']['top']
    upperback.stroke = text['upperback']['stroke']
    upperback.strokeWidth = text['upperback']['strokeWidth']
    upperback.save()
    design.upper_back_text = upperback

    if design.middle_back_text != None:
        design.middle_back_text.delete()
    middleback = Text()
    middleback.textvalue = text['middleback']['textvalue']
    middleback.fontFamily = text['middleback']['fontFamily']
    middleback.fill = text['middleback']['fill']
    middleback.fontStyle = text['middleback']['fontStyle']
    middleback.fontSize = text['middleback']['fontSize']
    middleback.left = text['middleback']['left']
    middleback.top = text['middleback']['top']
    middleback.stroke = text['middleback']['stroke']
    middleback.strokeWidth = text['middleback']['strokeWidth']
    middleback.save()
    design.middle_back_text = middleback

    if design.lower_back_text != None:
        design.lower_back_text.delete()
    lowerback = Text()
    lowerback.textvalue = text['lowerback']['textvalue']
    lowerback.fontFamily = text['lowerback']['fontFamily']
    lowerback.fill = text['lowerback']['fill']
    lowerback.fontStyle = text['lowerback']['fontStyle']
    lowerback.fontSize = text['lowerback']['fontSize']
    lowerback.left = text['lowerback']['left']
    lowerback.top = text['lowerback']['top']
    lowerback.stroke = text['lowerback']['stroke']
    lowerback.strokeWidth = text['lowerback']['strokeWidth']
    lowerback.save()
    design.lower_back_text = lowerback

    if design.front_logo != None:
        design.front_logo.delete()
    frontlogo = Logo()
    frontlogo.src = logo['front']['src']
    frontlogo.left = logo['front']['left']
    frontlogo.top = logo['front']['top']
    frontlogo.save()
    design.front_logo = frontlogo

    if design.back_logo != None:
        design.back_logo.delete()
    backlogo = Logo()
    backlogo.src = logo['back']['src']
    backlogo.left = logo['back']['left']
    backlogo.top = logo['back']['top']
    backlogo.save()
    design.back_logo = backlogo

def copy_text_and_logo(post_design, design):
    frontchest = Text()
    frontchest.textvalue = design.front_chest_text.textvalue
    frontchest.fontFamily = design.front_chest_text.fontFamily
    frontchest.fill = design.front_chest_text.fill
    frontchest.fontStyle = design.front_chest_text.fontStyle
    frontchest.fontSize = design.front_chest_text.fontSize
    frontchest.left = design.front_chest_text.left
    frontchest.top = design.front_chest_text.top
    frontchest.stroke = design.front_chest_text.stroke
    frontchest.strokeWidth = design.front_chest_text.strokeWidth
    frontchest.save()
    post_design.front_chest_text = frontchest
    
    rightarm = Text()
    rightarm.textvalue = design.right_arm_text.textvalue
    rightarm.fontFamily = design.right_arm_text.fontFamily
    rightarm.fill = design.right_arm_text.fill
    rightarm.fontStyle = design.right_arm_text.fontStyle
    rightarm.fontSize = design.right_arm_text.fontSize
    rightarm.left = design.right_arm_text.left
    rightarm.top = design.right_arm_text.top
    rightarm.stroke = design.right_arm_text.stroke
    rightarm.strokeWidth = design.right_arm_text.strokeWidth
    rightarm.save()
    post_design.right_arm_text = rightarm

    upperback = Text()
    upperback.textvalue = design.upper_back_text.textvalue
    upperback.fontFamily = design.upper_back_text.fontFamily
    upperback.fill = design.upper_back_text.fill
    upperback.fontStyle = design.upper_back_text.fontStyle
    upperback.fontSize = design.upper_back_text.fontSize
    upperback.left = design.upper_back_text.left
    upperback.top = design.upper_back_text.top
    upperback.stroke = design.upper_back_text.stroke
    upperback.strokeWidth = design.upper_back_text.strokeWidth
    upperback.save()
    post_design.upper_back_text = upperback

    middleback = Text()
    middleback.textvalue = design.middle_back_text.textvalue
    middleback.fontFamily = design.middle_back_text.fontFamily
    middleback.fill = design.middle_back_text.fill
    middleback.fontStyle = design.middle_back_text.fontStyle
    middleback.fontSize = design.middle_back_text.fontSize
    middleback.left = design.middle_back_text.left
    middleback.top = design.middle_back_text.top
    middleback.stroke = design.middle_back_text.stroke
    middleback.strokeWidth = design.middle_back_text.strokeWidth
    middleback.save()
    post_design.middle_back_text = middleback

    lowerback = Text()
    lowerback.textvalue = design.lower_back_text.textvalue
    lowerback.fontFamily = design.lower_back_text.fontFamily
    lowerback.fill = design.lower_back_text.fill
    lowerback.fontStyle = design.lower_back_text.fontStyle
    lowerback.fontSize = design.lower_back_text.fontSize
    lowerback.left = design.lower_back_text.left
    lowerback.top = design.lower_back_text.top
    lowerback.stroke = design.lower_back_text.stroke
    lowerback.strokeWidth = design.lower_back_text.strokeWidth
    lowerback.save()
    post_design.lower_back_text = lowerback

    frontlogo = Logo()
    frontlogo.src = design.front_logo.src
    frontlogo.left = design.front_logo.left
    frontlogo.top = design.front_logo.top
    frontlogo.save()
    post_design.front_logo = frontlogo

    backlogo = Logo()
    backlogo.src = design.back_logo.src
    backlogo.left = design.back_logo.left
    backlogo.top = design.back_logo.top
    backlogo.save()
    post_design.back_logo = backlogo

@csrf_exempt
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes((IsAuthenticatedOrGETDELETEOnly,))
def main(request):    
    if request.method == 'GET':
        # check if user is logged in
        if request.user.id == None: 
            design = Design()
        else:
            try:
                user = Profile.objects.get(user=request.user)
            except Profile.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)    

            design = user.recent
            # if there is no design user is working on, create a new one
            if design == None:
                design = Design()
                design.owner = request.user
                design.group = user.user_group
                design.name = 'new_design_'+str(user.number)
                design.save()
                user.recent = design
                user.number += 1
                user.save()
        set_default_text_and_logo(design, request.user.id != None)
        design_serializer = UserDesignSerializer(design)
        return Response(design_serializer.data)
    
    # saves design to user group
    if request.method == 'PUT':
        try:
            user = Profile.objects.get(user=request.user)
        except Profile.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)    

        data = json.loads(request.body.decode("utf-8")) 
        design_id=data['id']
        if design_id != user.recent.id:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        user.recent.name=data['name']
        user.recent.body=data['design']['body']
        user.recent.sleeve=data['design']['sleeve']
        user.recent.button=data['design']['button']
        user.recent.banding=data['design']['banding']
        user.recent.stripe=data['design']['stripe']
        update_text_and_logo(data['text'], data['logo'], user.recent)
        user.recent.front_image_url=data['image']['frontImg']
        user.recent.back_image_url=data['image']['backImg']
        user.recent.save()
        design_serializer = UserDesignSerializer(user.recent)
        return Response(design_serializer.data)

    # doesn't really delete design but saves it in user group
    # needs to be deleted in user group detail
    if request.method == 'DELETE':
        if request.user.id == None: 
            design = Design()
        else:    
            try:
                user = Profile.objects.get(user=request.user)
            except Profile.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)
            
            design = Design()
            design.owner = request.user
            design.group = user.user_group
            design.name = 'new_design_'+str(user.number)
            design.save()
            user.recent = design
            user.number += 1
            user.save()
            
        set_default_text_and_logo(design, request.user.id != None)
        design_serializer = UserDesignSerializer(design)
        return Response(design_serializer.data)

    # # save design and copys design to requested group
    # if request.method == 'POST':
    #     design_id=request.data['id']
    #     if design_id != user.recent.id:
    #         return Response(status=status.HTTP_400_BAD_REQUEST)
    #     user.recent.detail_body=request.data['detail_body']
    #     user.recent.detail_sleeve=request.data['detail_sleeve']
        # user.recent.detail_buttons=request.data['detail_buttons']
        # user.recent.detail_banding=request.data['detail_banding']
        # user.recent.detail_stripes=request.data['detail_stripes']
    #     user.recent.save()

    #     try:
    #         group = Group.objects.get(id=request.data['group'])
    #     except Group.DoesNotExist:
    #         return Response(status=status.HTTP_400_BAD_REQUEST)
    #     if request.user not in group.users.all():
    #         return Response(status=status.HTTP_403_FORBIDDEN)
        
    #     post_design=Design()
    #     post_design.owner = request.user
    #     post_design.group = group
    #     post_design.detail_body = request.data['detail_body']
    #     post_design.detail_sleeve = request.data['detail_sleeve']
    # post_design.detail_buttons=request.data['detail_buttons']
        # post_design.detail_banding=request.data['detail_banding']
        # post_design.detail_stripes=request.data['detail_stripes']
    #     post_design.save()

    #     design_serializer = UserDesignSerializer(user.recent)
    #     return Response(design_serializer.data)

@api_view(['GET'])
@permission_classes((IsAuthenticatedOrNothing,))
def post_design(request, group_id, design_id):
    # copys design to requested group
    if request.method == 'GET':
        try:
            group = Group.objects.get(id=group_id)
        except Group.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if request.user not in group.users.all():
            return Response(status=status.HTTP_403_FORBIDDEN)
        
        try:
            design = Design.objects.get(id=design_id)
        except Design.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)        

        post_design=Design()
        post_design.name = design.name
        post_design.owner = request.user
        post_design.group = group
        post_design.body = design.body
        post_design.sleeve = design.sleeve
        post_design.button = design.button
        post_design.banding = design.banding
        post_design.stripe = design.stripe
        copy_text_and_logo(post_design, design)
        post_design.front_image_url = design.front_image_url
        post_design.back_image_url = design.back_image_url
        post_design.save()

        design_serializer = UserDesignSerializer(post_design)
        return Response(design_serializer.data)

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
            designs = Design.objects.all().filter(group=group).annotate(likes=Count('who')).order_by('-likes')
        except Design.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        design_serializer = GroupDesignSerializer(designs, user=request.user, many=True)
        
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
        
        if data['grouptype'] == 'UR':
            return Response(status=status.HTTP_403_FORBIDDEN)
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
        if group.group_type == 'UR':
            return Response(status=status.HTTP_400_BAD_REQUEST)
            
        if request.user.id == None:
            return Response(status=status.HTTP_403_FORBIDDEN)
        try:
            user = User.objects.get(username=request.user)
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        if user in group.users.all():
            return Response(status=status.HTTP_400_BAD_REQUEST)
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

@api_view(['GET', 'PUT'])
@permission_classes((IsAuthenticatedOrNothing,))
def edit_design(request, design_id):
    if request.user.id == None:
        return Response(status=status.HTTP_403_FORBIDDEN)
    try:
        user = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        return Response(status=status.HTTP_403_FORBIDDEN)

    try:
        design = Design.objects.get(id=design_id)
    except Design.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if request.user != design.owner:
        return Response(status=status.HTTP_403_FORBIDDEN)
    
    if request.method == 'GET':
        if design.group.group_type != 'UR' or request.user not in design.group.master.all():
            return Response(status=status.HTTP_403_FORBIDDEN)
        
        user.recent = design
        user.save()
        profile_serializer = ProfileSerializer(user)
        return Response(profile_serializer.data)
    
    if request.method == 'PUT':
        data = json.loads(request.body.decode("utf-8")) 
        design.name = data['name']
        design.save()
        design_serializer = UserDesignSerializer(design)
        return Response(design_serializer.data)

@csrf_exempt
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes((IsAuthenticatedOrNothing,))
def update_group(request, group_id):
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

    if request.method == 'GET':
        groups = Group.objects.filter(id=group_id)
        group_serializer = GroupSerializer(instance=groups, many=True)
        return Response(group_serializer.data)

    if user not in group.master.all():
        return Response(status=status.HTTP_403_FORBIDDEN)

    if request.method == 'PUT':
        group_name=request.data['group_name']
        group_type=request.data['group_type']

        if group_type=='UR':
            return Response(status = status.HTTP_403_FORBIDDEN)
        try: # if there is a group that has same groupname, return 409
            old_group = Group.objects.get(group_name = group_name)
            return Response(status = status.HTTP_409_CONFLICT)
        except Group.DoesNotExist:
            pass
        
        group.group_type = group_type
        group.group_name = group_name
        group.save()
        
        groups = Group.objects.filter(id=group_id)
        group_serializer = GroupSerializer(instance=groups, many=True)
        return Response(group_serializer.data)

    if request.method == 'DELETE':
        group.delete()
        return Response(status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes((IsAuthenticatedOrNothing,))
def member_list(request, group_id):
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
    if user not in group.master.all():
        return Response(status=status.HTTP_403_FORBIDDEN)
    
    if request.method == 'GET':
        member_serializer = MemberSerializer(instance=group.users, group=group, many=True)
        return Response(member_serializer.data)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes((IsAuthenticatedOrNothing,))
def update_member(request, group_id, user_id):
    if request.user.id == None:
        return Response(status=status.HTTP_403_FORBIDDEN)
    
    try:
        group = Group.objects.get(id=group_id)
    except Group.DoesNotExist:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    if request.user not in group.master.all():
        return Response(status=status.HTTP_403_FORBIDDEN)
    
    try:
        target_user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if target_user not in group.users.all():
        return Response(status=status.HTTP_400_BAD_REQUEST)
    
    if request.method == 'GET':
        return Response(status=status.HTTP_200_OK)
    if request.method == 'PUT':
        if target_user not in group.master.all():
            group.master.add(target_user)
    
    if request.method == 'DELETE':
        if target_user == request.user:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        group.users.remove(target_user)
        if target_user in group.master.all():
            group.master.remove(target_user)
    
    member_serializer = MemberSerializer(instance=group.users, group=group, many=True)
    return Response(member_serializer.data)

@api_view(['GET',])
@permission_classes((IsAuthenticatedOrNothing,))
def drop_group(request, group_id):
    if request.user.id == None:
        return Response(status=status.HTTP_403_FORBIDDEN)
    
    try:
        group = Group.objects.get(id=group_id)
    except Group.DoesNotExist:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    if request.user not in group.users.all():
        return Response(status=status.HTTP_403_FORBIDDEN)
    
    if request.method == 'GET':
        if request.user in group.master.all() and group.master.all().count()<=1:
            return Response(status=status.HTTP_406_NOT_ACCEPTABLE)
        group.users.remove(request.user)
        if request.user in group.master.all():
            group.master.remove(request.user)
    
    return Response(status=status.HTTP_202_ACCEPTED)

@api_view(['GET'])
@permission_classes((IsAuthenticatedOrNothing,))
def update_likes(request, design_id):
    if request.method == 'GET':
        if request.user.id == None:
            return Response(status=status.HTTP_403_FORBIDDEN)
        try:
            user = User.objects.get(username=request.user)
        except User.DoesNotExist:
            return Response(status=status.HTTP_403_FORBIDDEN)
        
        try:
            design = Design.objects.get(id=design_id)
        except Design.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if request.user not in design.group.users.all():
            return Response(status=status.HTTP_403_FORBIDDEN)
        if request.user in design.who.all():
            return Response(status=status.HTTP_406_NOT_ACCEPTABLE)
        
        design.who.add(user)
        design.save()
        design_serializer = UserDesignSerializer(design)
        return Response(design_serializer.data)

@api_view(['GET'])
@permission_classes((IsAuthenticatedOrNothing,))
def undo_likes(request, design_id):
    if request.method == 'GET':
        if request.user.id == None:
            return Response(status=status.HTTP_403_FORBIDDEN)
        try:
            user = User.objects.get(username=request.user)
        except User.DoesNotExist:
            return Response(status=status.HTTP_403_FORBIDDEN)
        
        try:
            design = Design.objects.get(id=design_id)
        except Design.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if request.user not in design.group.users.all():
            return Response(status=status.HTTP_403_FORBIDDEN)
        if request.user not in design.who.all():
            return Response(status=status.HTTP_406_NOT_ACCEPTABLE)
        
        design.who.remove(user)
        design.save()
        design_serializer = UserDesignSerializer(design)
        return Response(design_serializer.data)

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

@api_view(['GET'])
@permission_classes((IsAuthenticatedOrNothing,))
def delete_design(request, design_id):
    if request.method == 'GET':
        if request.user.id == None:
            return Response(status=status.HTTP_403_FORBIDDEN)
        try:
            user = User.objects.get(username=request.user)
        except User.DoesNotExist:
            return Response(status=status.HTTP_403_FORBIDDEN)
        
        try:
            design = Design.objects.get(id=design_id)
        except Design.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if request.user not in design.group.master.all() and request.user != design.owner:
            return Response(status=status.HTTP_403_FORBIDDEN)
    
        design.delete()

        return Response(status=status.HTTP_200_OK)

@csrf_exempt
@api_view(['GET', 'POST'])
@permission_classes((IsAuthenticatedOrGETOnly,))
def add_comment(request, design_id):
    try:
        design = Design.objects.get(id=design_id)
    except Design.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'POST':
        comment = Comment()
        comment.writer = request.user
        comment.design = design
        comment.name = request.data['name']
        comment.comment = request.data['comment']
        comment.save()
    
    c_set = Comment.objects.all().filter(design=design).order_by('created_at').reverse()
    return Response(CommentSerializer(c_set, user=request.user, many=True).data)

@api_view(['GET', 'DELETE', 'PUT'])
@permission_classes((IsAuthenticatedOrGETOnly,))
def update_comment(request, design_id, comment_id):
    try:
        comment = Comment.objects.get(id=comment_id)
    except Comment.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    try:
        design = Design.objects.get(id=design_id)
    except Design.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if comment.design != design:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    if comment.writer != request.user and request.user not in comment.design.group.master.all():
        return Response(status=status.HTTP_403_FORBIDDEN)
    if request.method == 'DELETE':
        comment.delete()
    if request.method == 'PUT':
        comment.name = request.data['name']
        comment.comment = request.data['comment']
        comment.save()

    c_set = Comment.objects.all().filter(design=design).order_by('created_at').reverse()
    return Response(CommentSerializer(c_set, user=request.user, many=True).data)

@api_view(['GET'])
@permission_classes((IsAuthenticatedOrNothing,))
def comment_like(request, comment_id):
    if request.method == 'GET':
        if request.user.id == None:
            return Response(status=status.HTTP_403_FORBIDDEN)
        try:
            user = User.objects.get(username=request.user)
        except User.DoesNotExist:
            return Response(status=status.HTTP_403_FORBIDDEN)
        
        try:
            comment = Comment.objects.get(id=comment_id)
        except Comment.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        if request.user in comment.who_c.all():
            return Response(status=status.HTTP_406_NOT_ACCEPTABLE)
        
        comment.who_c.add(user)
        comment.save()
        
        c_set = Comment.objects.all().filter(design=comment.design).order_by('created_at').reverse()
        return Response(CommentSerializer(c_set, user=request.user, many=True).data)

@api_view(['GET'])
@permission_classes((IsAuthenticatedOrNothing,))
def comment_unlike(request, comment_id):
    if request.method == 'GET':
        if request.user.id == None:
            return Response(status=status.HTTP_403_FORBIDDEN)
        try:
            user = User.objects.get(username=request.user)
        except User.DoesNotExist:
            return Response(status=status.HTTP_403_FORBIDDEN)
        
        try:
            comment = Comment.objects.get(id=comment_id)
        except Comment.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        if request.user not in comment.who_c.all():
            return Response(status=status.HTTP_406_NOT_ACCEPTABLE)
        
        comment.who_c.remove(user)
        comment.save()
        
        c_set = Comment.objects.all().filter(design=comment.design).order_by('created_at').reverse()
        return Response(CommentSerializer(c_set, user=request.user, many=True).data)

@api_view(['GET'])
@permission_classes((IsAuthenticatedOrNothing,))
def get_profile(request):
    if request.method == 'GET':
        if request.user.id == None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        try:
            profile = Profile.objects.get(user=request.user)
        except Profile.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        profile_serializer = ProfileSerializer(profile)
        return Response(profile_serializer.data)
