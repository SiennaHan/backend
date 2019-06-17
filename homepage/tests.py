from django.test import TestCase, Client
from django.contrib.auth.models import User
from .default_logo import DEFAULT_LOGO_BASE64
from .default_image_url import DEFAULT_IMG_FRONT_URL, DEFAULT_IMG_BACK_URL
from .models import *
from .views import *

from base64 import b64encode as encode
import io


##########################################################
#################### Test Member Page ####################
##########################################################

## Member Join
class UserJoinCase(TestCase):
    # Member 
    def test_join(self):
        # if there is an user that has same username, test fails(unlikely)
        try:
            user = User.objects.get(username='join')
            self.assertEqual(1, 2)
        except User.DoesNotExist:
            pass
        response = self.client.post('/users/', {'username': 'join', 'password': 'pass'})
        self.assertEqual(response.status_code//100, 2)
        
        ## User Object Check
        try:
            user = User.objects.get(username='join')
        except User.DoesNotExist:
            self.assertEqual(1, 2)
        self.assertEqual(user.username, 'join')
        self.assertFalse(user.id==None)
        
        ## User Group Check
        try:
            group = Group.objects.get(group_name='user_group_join')
        except User.DoesNotExist:
            self.assertEqual(1, 2)
        self.assertEqual(group.group_type, 'UR')
        self.assertEqual(group.group_name, 'user_group_join')
        self.assertTrue(user in group.master.all())
        self.assertFalse(group.id==None)
        

        ## Profile Object Check
        try:
            profile = Profile.objects.get(user=user)
        except Profile.DoesNotExist:
            self.assertEqual(1, 2)
        self.assertEqual(profile.user.username, 'join')
        self.assertTrue(profile.recent==None)
        self.assertTrue(group in profile.groups.all())
    
    # Member Join with Duplicates
    def test_with_dups(self):
        # if there is an user that has same username, test fails(unlikely)
        try:
            user = User.objects.get(username='join_dup')
            self.assertEqual(1, 2)
        except User.DoesNotExist:
            pass
        response = self.client.post('/users/', {'username': 'join_dup', 'password': 'pass'})
        self.assertEqual(response.status_code//100, 2)

        # if there is an user that has same username, test fails(unlikely)
        try:
            user = User.objects.get(username='join_dup')
        except User.DoesNotExist:
            self.assertEqual(1, 2)
        response = self.client.post('/users/', {'username': 'join_dup', 'password': 'pass'})
        self.assertEqual(response.status_code//100, 4)

## Member Login
class UserLoginCase(TestCase):
    def setUp(self):
        self.client.post('/users/', {'username': 'login', 'password': 'pass'})
    
    # Login Fail
    # Login Success
    def test_login(self):
        # Wrong Password
        credentials = encode(b'login:passwd')
        response = self.client.get('/auth/', HTTP_AUTHORIZATION='Basic ' + credentials.decode())
        self.assertEqual(response.status_code//100, 4)

        # Correct Password
        credentials = encode(b'login:pass')
        response = self.client.get('/auth/', HTTP_AUTHORIZATION='Basic ' + credentials.decode())
        self.assertEqual(response.status_code//100, 2)

## Member Profile
class UserProfile(TestCase):
    def setUp(self):
        self.client.post('/users/', {'username': 'profile', 'password': 'pass'})

    # User Profile without Login
    def test_without_auth(self):
        self.client.logout()
        response = self.client.get('/users/profile/')
        self.assertEqual(response.status_code//100, 4)
    
    # Get User Info
    def test_get_info(self):
        self.client.login(username='profile',password='pass')
        response = self.client.get('/users/profile/')
        self.assertEqual(response.status_code//100, 2)
        response.render()
        stream = io.BytesIO(response.content)
        data = JSONParser().parse(stream)
        self.assertEqual(data['username'], 'profile')

    # Change Password / Login
    def test_change_pw(self):
        self.client.login(username='profile',password='pass')
        response = self.client.get('/users/profile/')
        response.render()
        stream = io.BytesIO(response.content)
        data = JSONParser().parse(stream)
        response = self.client.put('/users/profile/', """{
            \"id\": """ + str(data['id']) + """,
            \"username\": \"profile\",
            \"password\": \"passwd\"
            }""",
            content_type='application/json')
        self.assertEqual(response.status_code//100, 2)
        self.client.logout()
        credentials = encode(b'profile:pass')
        response = self.client.get('/auth/', HTTP_AUTHORIZATION='Basic ' + credentials.decode())
        self.assertEqual(response.status_code//100, 4)
        credentials = encode(b'profile:passwd')
        response = self.client.get('/auth/', HTTP_AUTHORIZATION='Basic ' + credentials.decode())
        self.assertEqual(response.status_code//100, 2)

##########################################################
#################### Test Design Page ####################
##########################################################

## Default Design
class DefaultDesignCase(TestCase):
    def setUp(self):
        self.client.post('/users/', {'username': 'default', 'password': 'pass'})
    
    # Default Design without Login
    def test_without_auth(self):
        self.client.logout()
        response = self.client.get('/')
        self.assertEqual(response.status_code//100, 2)
        response.render()
        stream = io.BytesIO(response.content)
        data = JSONParser().parse(stream)
        self.assertEqual(data['design']['sleeve'], '#fcfcfc')
        self.assertEqual(data['design']['body'], '#001c58')
        self.assertEqual(data['design']['button'], '#fcfcfc')
        self.assertEqual(data['design']['banding'], '#001c58')
        self.assertEqual(data['design']['stripe'], '#fcfcfc')
        self.assertEqual(data['text']['frontchest']['textvalue'], "S")
        self.assertEqual(data['text']['frontchest']['fontFamily'], "arial")
        self.assertEqual(data['text']['frontchest']['fill'], "#3f51b5")
        self.assertEqual(data['text']['frontchest']['fontStyle'], "bold")
        self.assertEqual(data['text']['frontchest']['fontSize'], 50)
        self.assertEqual(data['text']['frontchest']['left'], 250)
        self.assertEqual(data['text']['frontchest']['top'], 110)
        self.assertEqual(data['text']['frontchest']['stroke'], "#000000")
        self.assertEqual(data['text']['frontchest']['strokeWidth'], 2)
        self.assertEqual(data['text']['rightarm']['textvalue'],"19")
        self.assertEqual(data['text']['rightarm']['fontFamily'],"arial")
        self.assertEqual(data['text']['rightarm']['fill'],"#607d8b")
        self.assertEqual(data['text']['rightarm']['fontStyle'],"bold")
        self.assertEqual(data['text']['rightarm']['fontSize'],50)
        self.assertEqual(data['text']['rightarm']['left'],46)
        self.assertEqual(data['text']['rightarm']['top'],124)
        self.assertEqual(data['text']['rightarm']['stroke'],"")
        self.assertEqual(data['text']['rightarm']['strokeWidth'],0)
        self.assertEqual(data['text']['upperback']['textvalue'], "SEOUL NAT'L")
        self.assertEqual(data['text']['upperback']['fontFamily'], "arial")
        self.assertEqual(data['text']['upperback']['fill'], "#ffc107")
        self.assertEqual(data['text']['upperback']['fontStyle'], "bold")
        self.assertEqual(data['text']['upperback']['fontSize'], 25)
        self.assertEqual(data['text']['upperback']['left'], 135)
        self.assertEqual(data['text']['upperback']['top'], 125)
        self.assertEqual(data['text']['upperback']['stroke'], "")
        self.assertEqual(data['text']['upperback']['strokeWidth'], 0)
        self.assertEqual(data['text']['middleback']['textvalue'], "UNIVERSITY")
        self.assertEqual(data['text']['middleback']['fontFamily'], "arial")
        self.assertEqual(data['text']['middleback']['fill'], "#ffc107")
        self.assertEqual(data['text']['middleback']['fontStyle'], "bold")
        self.assertEqual(data['text']['middleback']['fontSize'], 20)
        self.assertEqual(data['text']['middleback']['left'], 155)
        self.assertEqual(data['text']['middleback']['top'], 155)
        self.assertEqual(data['text']['middleback']['stroke'], "")
        self.assertEqual(data['text']['middleback']['strokeWidth'], 0)
        self.assertEqual(data['text']['lowerback']['textvalue'], "Department of\nComputer Science")
        self.assertEqual(data['text']['lowerback']['fontFamily'], "arial")
        self.assertEqual(data['text']['lowerback']['fill'], "#ffc107")
        self.assertEqual(data['text']['lowerback']['fontStyle'], "italic")
        self.assertEqual(data['text']['lowerback']['fontSize'], 15)
        self.assertEqual(data['text']['lowerback']['left'], 151)
        self.assertEqual(data['text']['lowerback']['top'], 256)
        self.assertEqual(data['text']['lowerback']['stroke'], "")
        self.assertEqual(data['text']['lowerback']['strokeWidth'], 0)
        self.assertEqual(data['logo']['front']['src'], DEFAULT_LOGO_BASE64)
        self.assertEqual(data['logo']['front']['width'], 571)
        self.assertEqual(data['logo']['front']['height'], 589)
        self.assertEqual(data['logo']['front']['left'], 357)
        self.assertEqual(data['logo']['front']['top'], 152)
        self.assertEqual(data['logo']['front']['scaleX'], 1)
        self.assertEqual(data['logo']['front']['scaleY'], 1)
        self.assertEqual(data['logo']['back']['src'], DEFAULT_LOGO_BASE64)
        self.assertEqual(data['logo']['back']['width'], 571)
        self.assertEqual(data['logo']['back']['height'], 589)
        self.assertEqual(data['logo']['back']['left'], 212)
        self.assertEqual(data['logo']['back']['top'], 216)
        self.assertEqual(data['logo']['back']['scaleX'], 1)
        self.assertEqual(data['logo']['back']['scaleY'], 1)
        self.assertEqual(data['image']['frontImg'], DEFAULT_IMG_FRONT_URL)
        self.assertEqual(data['image']['backImg'], DEFAULT_IMG_BACK_URL)
        self.assertEqual(data['likes'], 0)
        # id, group, owner should be null for non-authorized requests
        self.assertEqual(data['id'], None)
        self.assertEqual(data['group'], None)
        # these ids should be null for unsaved designs
        self.assertEqual(data['text']['frontchest']['id'], None)
        self.assertEqual(data['text']['rightarm']['id'], None)
        self.assertEqual(data['text']['upperback']['id'], None)
        self.assertEqual(data['text']['middleback']['id'], None)
        self.assertEqual(data['text']['lowerback']['id'], None)
        self.assertEqual(data['logo']['front']['id'], None)
        self.assertEqual(data['logo']['back']['id'], None)

    # Default Design after Login
    def test_default_design(self):
        self.client.login(username='default',password='pass')
        response = self.client.get('/')
        self.assertEqual(response.status_code//100, 2)
        response.render()
        stream = io.BytesIO(response.content)
        data = JSONParser().parse(stream)
        self.assertEqual(data['design']['sleeve'], '#fcfcfc')
        self.assertEqual(data['design']['body'], '#001c58')
        self.assertEqual(data['design']['button'], '#fcfcfc')
        self.assertEqual(data['design']['banding'], '#001c58')
        self.assertEqual(data['design']['stripe'], '#fcfcfc')
        self.assertEqual(data['text']['frontchest']['textvalue'], "S")
        self.assertEqual(data['text']['frontchest']['fontFamily'], "arial")
        self.assertEqual(data['text']['frontchest']['fill'], "#3f51b5")
        self.assertEqual(data['text']['frontchest']['fontStyle'], "bold")
        self.assertEqual(data['text']['frontchest']['fontSize'], 50)
        self.assertEqual(data['text']['frontchest']['left'], 250)
        self.assertEqual(data['text']['frontchest']['top'], 110)
        self.assertEqual(data['text']['frontchest']['stroke'], "#000000")
        self.assertEqual(data['text']['frontchest']['strokeWidth'], 2)
        self.assertEqual(data['text']['rightarm']['textvalue'],"19")
        self.assertEqual(data['text']['rightarm']['fontFamily'],"arial")
        self.assertEqual(data['text']['rightarm']['fill'],"#607d8b")
        self.assertEqual(data['text']['rightarm']['fontStyle'],"bold")
        self.assertEqual(data['text']['rightarm']['fontSize'],50)
        self.assertEqual(data['text']['rightarm']['left'],46)
        self.assertEqual(data['text']['rightarm']['top'],124)
        self.assertEqual(data['text']['rightarm']['stroke'],"")
        self.assertEqual(data['text']['rightarm']['strokeWidth'],0)
        self.assertEqual(data['text']['upperback']['textvalue'], "SEOUL NAT'L")
        self.assertEqual(data['text']['upperback']['fontFamily'], "arial")
        self.assertEqual(data['text']['upperback']['fill'], "#ffc107")
        self.assertEqual(data['text']['upperback']['fontStyle'], "bold")
        self.assertEqual(data['text']['upperback']['fontSize'], 25)
        self.assertEqual(data['text']['upperback']['left'], 135)
        self.assertEqual(data['text']['upperback']['top'], 125)
        self.assertEqual(data['text']['upperback']['stroke'], "")
        self.assertEqual(data['text']['upperback']['strokeWidth'], 0)
        self.assertEqual(data['text']['middleback']['textvalue'], "UNIVERSITY")
        self.assertEqual(data['text']['middleback']['fontFamily'], "arial")
        self.assertEqual(data['text']['middleback']['fill'], "#ffc107")
        self.assertEqual(data['text']['middleback']['fontStyle'], "bold")
        self.assertEqual(data['text']['middleback']['fontSize'], 20)
        self.assertEqual(data['text']['middleback']['left'], 155)
        self.assertEqual(data['text']['middleback']['top'], 155)
        self.assertEqual(data['text']['middleback']['stroke'], "")
        self.assertEqual(data['text']['middleback']['strokeWidth'], 0)
        self.assertEqual(data['text']['lowerback']['textvalue'], "Department of\nComputer Science")
        self.assertEqual(data['text']['lowerback']['fontFamily'], "arial")
        self.assertEqual(data['text']['lowerback']['fill'], "#ffc107")
        self.assertEqual(data['text']['lowerback']['fontStyle'], "italic")
        self.assertEqual(data['text']['lowerback']['fontSize'], 15)
        1
        self.assertEqual(data['text']['lowerback']['top'], 256)
        self.assertEqual(data['text']['lowerback']['stroke'], "")
        self.assertEqual(data['text']['lowerback']['strokeWidth'], 0)
        self.assertEqual(data['logo']['front']['src'], DEFAULT_LOGO_BASE64)
        self.assertEqual(data['logo']['front']['width'], 571)
        self.assertEqual(data['logo']['front']['height'], 589)
        self.assertEqual(data['logo']['front']['left'], 357)
        self.assertEqual(data['logo']['front']['top'], 152)
        self.assertEqual(data['logo']['front']['scaleX'], 1)
        self.assertEqual(data['logo']['front']['scaleY'], 1)
        self.assertEqual(data['logo']['back']['src'], DEFAULT_LOGO_BASE64)
        self.assertEqual(data['logo']['back']['width'], 571)
        self.assertEqual(data['logo']['back']['height'], 589)
        self.assertEqual(data['logo']['back']['left'], 212)
        self.assertEqual(data['logo']['back']['top'], 216)
        self.assertEqual(data['logo']['back']['scaleX'], 1)
        self.assertEqual(data['logo']['back']['scaleY'], 1)
        self.assertEqual(data['image']['frontImg'], DEFAULT_IMG_FRONT_URL)
        self.assertEqual(data['image']['backImg'], DEFAULT_IMG_BACK_URL)
        self.assertEqual(data['likes'], 0)
        # id, group, owner should not be null for authorized requests
        design_id = data['id']
        self.assertFalse(design_id==None)
        self.assertEquals(Group.objects.get(id=data['group']).group_name, 'user_group_default')
        # these ids should be null for unsaved designs
        self.assertEqual(data['text']['frontchest']['id'], None)
        self.assertEqual(data['text']['rightarm']['id'], None)
        self.assertEqual(data['text']['upperback']['id'], None)
        self.assertEqual(data['text']['middleback']['id'], None)
        self.assertEqual(data['text']['lowerback']['id'], None)
        self.assertEqual(data['logo']['front']['id'], None)
        self.assertEqual(data['logo']['back']['id'], None)
        # this design should be set to recent
        user = User.objects.get(username='default')
        profile = Profile.objects.get(user=user)
        self.assertEqual(profile.recent.id, design_id)

## Design Save
class DesignSaveCase(TestCase):
    def setUp(self):
        self.client.post('/users/', {'username': 'save', 'password': 'pass'})

    # Save without Login
    def test_without_auth(self):
        self.client.logout()
        design_data = """{
            \"id\": null,
            \"design\": {
                \"body\": \"#fcfcfc\",
                \"button\": \"#fcfcfc\",
                \"sleeve\": \"#fcfcfc\",
                \"banding\": \"#fcfcfc\",
                \"stripe\": \"#fcfcfc\"
            },
            \"text\": {
                \"frontchest\": {
                    \"id\": null,
                    \"textvalue\": \"S\",
                    \"fontFamily\": \"arial\",
                    \"fill\": \"#3f51b5\",
                    \"fontStyle\": \"bold\",
                    \"fontSize\": 50,
                    \"left\": 250,
                    \"top\": 110,
                    \"stroke\": \"#000000\",
                    \"strokeWidth\": 2
                },
                \"rightarm\": {
                    \"id\": null,
                    \"textvalue\": \"19\",
                    \"fontFamily\": \"arial\",
                    \"fill\": \"#607d8b\",
                    \"fontStyle\": \"bold\",
                    \"fontSize\": 50,
                    \"left\": 50,
                    \"top\": 120,
                    \"stroke\": \"\",
                    \"strokeWidth\": 0
                },
                \"upperback\": {
                    \"id\": null,
                    \"textvalue\": \"SEOUL NAT'L\",
                    \"fontFamily\": \"arial\",
                    \"fill\": \"#ffc107\",
                    \"fontStyle\": \"bold\",
                    \"fontSize\": 25,
                    \"left\": 135,
                    \"top\": 125,
                    \"stroke\": \"\",
                    \"strokeWidth\": 0
                },
                \"middleback\": {
                    \"id\": null,
                    \"textvalue\": \"UNIVERSITY\",
                    \"fontFamily\": \"arial\",
                    \"fill\": \"#ffc107\",
                    \"fontStyle\": \"bold\",
                    \"fontSize\": 20,
                    \"left\": 155,
                    \"top\": 155,
                    \"stroke\": \"\",
                    \"strokeWidth\": 0
                },
                \"lowerback\": {
                    \"id\": null,
                    \"textvalue\": \"hi\",
                    \"fontFamily\": \"arial\",
                    \"fill\": \"#ffc107\",
                    \"fontStyle\": \"bold\",
                    \"fontSize\": 15,
                    \"left\": 150,
                    \"top\": 190,
                    \"stroke\": \"\",
                    \"strokeWidth\": 0
                }
            },
            \"logo\": {
                \"front\": {
                    \"id\": null,
                    \"src\": \"hi\",
                    \"width\": 571,
                    \"height\": 589,
                    \"left\": 340,
                    \"top\": 180,
                    \"scaleX\": 1,
                    \"scaleY\": 1
                },
                \"back\": {
                    \"id\": null,
                    \"src\": \"hi\",
                    \"width\": 571,
                    \"height\": 589,
                    \"left\": 215,
                    \"top\": 280,
                    \"scaleX\": 1,
                    \"scaleY\": 1
                }
            },
            \"image\": {
                \"frontImg\": null,
                \"backImg\": null
            }
        }"""
        response = self.client.put(path='/', data=design_data, content_type='application/json')
        self.assertEqual(response.status_code//100, 4)

    # Save after Login
    def test_design_save(self):
        self.client.login(username='save',password='pass')
        response = self.client.get('/')
        response.render()
        stream = io.BytesIO(response.content)
        data = JSONParser().parse(stream)
        design_id = data['id']
        design_data = """{
            \"id\": """ + str(design_id) + """,
            \"design\": {
                \"body\": \"#fcfcfc\",
                \"button\": \"#fcfcfc\",
                \"sleeve\": \"#fcfcfc\",
                \"banding\": \"#fcfcfc\",
                \"stripe\": \"#fcfcfc\"
            },
            \"text\": {
                \"frontchest\": {
                    \"id\": null,
                    \"textvalue\": \"S\",
                    \"fontFamily\": \"arial\",
                    \"fill\": \"#3f51b5\",
                    \"fontStyle\": \"bold\",
                    \"fontSize\": 50,
                    \"left\": 250,
                    \"top\": 110,
                    \"stroke\": \"#000000\",
                    \"strokeWidth\": 2
                },
                \"rightarm\": {
                    \"id\": null,
                    \"textvalue\": \"19\",
                    \"fontFamily\": \"arial\",
                    \"fill\": \"#607d8b\",
                    \"fontStyle\": \"bold\",
                    \"fontSize\": 50,
                    \"left\": 50,
                    \"top\": 120,
                    \"stroke\": \"\",
                    \"strokeWidth\": 0
                },
                \"upperback\": {
                    \"id\": null,
                    \"textvalue\": \"SEOUL NAT'L\",
                    \"fontFamily\": \"arial\",
                    \"fill\": \"#ffc107\",
                    \"fontStyle\": \"bold\",
                    \"fontSize\": 25,
                    \"left\": 135,
                    \"top\": 125,
                    \"stroke\": \"\",
                    \"strokeWidth\": 0
                },
                \"middleback\": {
                    \"id\": null,
                    \"textvalue\": \"UNIVERSITY\",
                    \"fontFamily\": \"arial\",
                    \"fill\": \"#ffc107\",
                    \"fontStyle\": \"bold\",
                    \"fontSize\": 20,
                    \"left\": 155,
                    \"top\": 155,
                    \"stroke\": \"\",
                    \"strokeWidth\": 0
                },
                \"lowerback\": {
                    \"id\": null,
                    \"textvalue\": \"hi\",
                    \"fontFamily\": \"arial\",
                    \"fill\": \"#ffc107\",
                    \"fontStyle\": \"bold\",
                    \"fontSize\": 15,
                    \"left\": 150,
                    \"top\": 190,
                    \"stroke\": \"\",
                    \"strokeWidth\": 0
                }
            },
            \"logo\": {
                \"front\": {
                    \"id\": null,
                    \"src\": \"hi\",
                    \"width\": 571,
                    \"height\": 589,
                    \"left\": 340,
                    \"top\": 180,
                    \"scaleX\": 1,
                    \"scaleY\": 1
                },
                \"back\": {
                    \"id\": null,
                    \"src\": \"hi\",
                    \"width\": 571,
                    \"height\": 589,
                    \"left\": 215,
                    \"top\": 280,
                    \"scaleX\": 1,
                    \"scaleY\": 1
                }
            },
            \"image\": {
                \"frontImg\": \"hi\",
                \"backImg\": \"hi\"
            }
        }"""
        self.client.put(path='/', data=design_data, content_type='application/json')
        response = self.client.get('/')
        response.render()
        stream = io.BytesIO(response.content)
        data = JSONParser().parse(stream)
        self.assertEqual(response.status_code//100, 2)
        self.assertEqual(data['design']['body'], '#fcfcfc')
        self.assertEqual(data['design']['banding'], '#fcfcfc')
        self.assertEqual(data['text']['lowerback']['textvalue'], "hi")
        self.assertEqual(data['logo']['front']['src'], "hi")
        self.assertEqual(data['logo']['back']['src'], "hi")
        self.assertEqual(data['image']['frontImg'], "hi")
        self.assertEqual(data['image']['backImg'], "hi")
        self.assertEqual(data['likes'], 0)
        # id should not change
        self.assertEqual(data['id'], design_id)
        # these ids should not be null for saved designs
        self.assertFalse(data['text']['frontchest']['id'] == None)
        self.assertFalse(data['text']['rightarm']['id'] == None)
        self.assertFalse(data['text']['upperback']['id'] == None)
        self.assertFalse(data['text']['middleback']['id'] == None)
        self.assertFalse(data['text']['lowerback']['id'] == None)
        self.assertFalse(data['logo']['front']['id'] == None)
        self.assertFalse(data['logo']['back']['id'] == None)
        # recent should not change
        user = User.objects.get(username='save')
        profile = Profile.objects.get(user=user)
        self.assertEqual(profile.recent.id, design_id)
    

## New Design
class NewDesignCase(TestCase):
    def setUp(self):
        self.client.post('/users/', {'username': 'newdesign', 'password': 'pass'})

    # New Design without Login
    def test_without_auth(self):
        self.client.logout()
        response = self.client.delete('/')
        self.assertEqual(response.status_code//100, 2)
        response.render()
        stream = io.BytesIO(response.content)
        data = JSONParser().parse(stream)
        self.assertEqual(data['design']['sleeve'], '#fcfcfc')
        self.assertEqual(data['design']['body'], '#001c58')
        self.assertEqual(data['design']['button'], '#fcfcfc')
        self.assertEqual(data['design']['banding'], '#001c58')
        self.assertEqual(data['design']['stripe'], '#fcfcfc')
        self.assertEqual(data['text']['frontchest']['textvalue'], "S")
        self.assertEqual(data['text']['frontchest']['fontFamily'], "arial")
        self.assertEqual(data['text']['frontchest']['fill'], "#3f51b5")
        self.assertEqual(data['text']['frontchest']['fontStyle'], "bold")
        self.assertEqual(data['text']['frontchest']['fontSize'], 50)
        self.assertEqual(data['text']['frontchest']['left'], 250)
        self.assertEqual(data['text']['frontchest']['top'], 110)
        self.assertEqual(data['text']['frontchest']['stroke'], "#000000")
        self.assertEqual(data['text']['frontchest']['strokeWidth'], 2)
        self.assertEqual(data['text']['rightarm']['textvalue'],"19")
        self.assertEqual(data['text']['rightarm']['fontFamily'],"arial")
        self.assertEqual(data['text']['rightarm']['fill'],"#607d8b")
        self.assertEqual(data['text']['rightarm']['fontStyle'],"bold")
        self.assertEqual(data['text']['rightarm']['fontSize'],50)
        self.assertEqual(data['text']['rightarm']['left'],46)
        self.assertEqual(data['text']['rightarm']['top'],124)
        self.assertEqual(data['text']['rightarm']['stroke'],"")
        self.assertEqual(data['text']['rightarm']['strokeWidth'],0)
        self.assertEqual(data['text']['upperback']['textvalue'], "SEOUL NAT'L")
        self.assertEqual(data['text']['upperback']['fontFamily'], "arial")
        self.assertEqual(data['text']['upperback']['fill'], "#ffc107")
        self.assertEqual(data['text']['upperback']['fontStyle'], "bold")
        self.assertEqual(data['text']['upperback']['fontSize'], 25)
        self.assertEqual(data['text']['upperback']['left'], 135)
        self.assertEqual(data['text']['upperback']['top'], 125)
        self.assertEqual(data['text']['upperback']['stroke'], "")
        self.assertEqual(data['text']['upperback']['strokeWidth'], 0)
        self.assertEqual(data['text']['middleback']['textvalue'], "UNIVERSITY")
        self.assertEqual(data['text']['middleback']['fontFamily'], "arial")
        self.assertEqual(data['text']['middleback']['fill'], "#ffc107")
        self.assertEqual(data['text']['middleback']['fontStyle'], "bold")
        self.assertEqual(data['text']['middleback']['fontSize'], 20)
        self.assertEqual(data['text']['middleback']['left'], 155)
        self.assertEqual(data['text']['middleback']['top'], 155)
        self.assertEqual(data['text']['middleback']['stroke'], "")
        self.assertEqual(data['text']['middleback']['strokeWidth'], 0)
        self.assertEqual(data['text']['lowerback']['textvalue'], "Department of\nComputer Science")
        self.assertEqual(data['text']['lowerback']['fontFamily'], "arial")
        self.assertEqual(data['text']['lowerback']['fill'], "#ffc107")
        self.assertEqual(data['text']['lowerback']['fontStyle'], "italic")
        self.assertEqual(data['text']['lowerback']['fontSize'], 15)
        1
        self.assertEqual(data['text']['lowerback']['top'], 256)
        self.assertEqual(data['text']['lowerback']['stroke'], "")
        self.assertEqual(data['text']['lowerback']['strokeWidth'], 0)
        self.assertEqual(data['logo']['front']['src'], DEFAULT_LOGO_BASE64)
        self.assertEqual(data['logo']['front']['width'], 571)
        self.assertEqual(data['logo']['front']['height'], 589)
        self.assertEqual(data['logo']['front']['left'], 357)
        self.assertEqual(data['logo']['front']['top'], 152)
        self.assertEqual(data['logo']['front']['scaleX'], 1)
        self.assertEqual(data['logo']['front']['scaleY'], 1)
        self.assertEqual(data['logo']['back']['src'], DEFAULT_LOGO_BASE64)
        self.assertEqual(data['logo']['back']['width'], 571)
        self.assertEqual(data['logo']['back']['height'], 589)
        self.assertEqual(data['logo']['back']['left'], 212)
        self.assertEqual(data['logo']['back']['top'], 216)
        self.assertEqual(data['logo']['back']['scaleX'], 1)
        self.assertEqual(data['logo']['back']['scaleY'], 1)
        self.assertEqual(data['image']['frontImg'], DEFAULT_IMG_FRONT_URL)
        self.assertEqual(data['image']['backImg'], DEFAULT_IMG_BACK_URL)
        self.assertEqual(data['likes'], 0)
        # id, group, owner should be null for non-authorized new requests
        self.assertEqual(data['id'], None)
        self.assertEqual(data['group'], None)
        # these ids should be null for unsaved new designs
        self.assertEqual(data['text']['frontchest']['id'], None)
        self.assertEqual(data['text']['rightarm']['id'], None)
        self.assertEqual(data['text']['upperback']['id'], None)
        self.assertEqual(data['text']['middleback']['id'], None)
        self.assertEqual(data['text']['lowerback']['id'], None)
        self.assertEqual(data['logo']['front']['id'], None)
        self.assertEqual(data['logo']['back']['id'], None)
        

    # New Design after Login
    def test_new_design(self):
        self.client.login(username='newdesign',password='pass')
        response = self.client.get('/')
        response.render()
        stream = io.BytesIO(response.content)
        data = JSONParser().parse(stream)
        design_id = data['id']
        response = self.client.delete('/')
        response = self.client.get('/')
        self.assertEqual(response.status_code//100, 2)
        response.render()
        stream = io.BytesIO(response.content)
        data = JSONParser().parse(stream)
        new_design_id = data['id']
        self.assertFalse(design_id == new_design_id)
        self.assertEqual(data['design']['sleeve'], '#fcfcfc')
        self.assertEqual(data['design']['body'], '#001c58')
        self.assertEqual(data['design']['button'], '#fcfcfc')
        self.assertEqual(data['design']['banding'], '#001c58')
        self.assertEqual(data['design']['stripe'], '#fcfcfc')
        self.assertEqual(data['text']['frontchest']['textvalue'], "S")
        self.assertEqual(data['text']['frontchest']['fontFamily'], "arial")
        self.assertEqual(data['text']['frontchest']['fill'], "#3f51b5")
        self.assertEqual(data['text']['frontchest']['fontStyle'], "bold")
        self.assertEqual(data['text']['frontchest']['fontSize'], 50)
        self.assertEqual(data['text']['frontchest']['left'], 250)
        self.assertEqual(data['text']['frontchest']['top'], 110)
        self.assertEqual(data['text']['frontchest']['stroke'], "#000000")
        self.assertEqual(data['text']['frontchest']['strokeWidth'], 2)
        self.assertEqual(data['text']['rightarm']['textvalue'],"19")
        self.assertEqual(data['text']['rightarm']['fontFamily'],"arial")
        self.assertEqual(data['text']['rightarm']['fill'],"#607d8b")
        self.assertEqual(data['text']['rightarm']['fontStyle'],"bold")
        self.assertEqual(data['text']['rightarm']['fontSize'],50)
        self.assertEqual(data['text']['rightarm']['left'],46)
        self.assertEqual(data['text']['rightarm']['top'],124)
        self.assertEqual(data['text']['rightarm']['stroke'],"")
        self.assertEqual(data['text']['rightarm']['strokeWidth'],0)
        self.assertEqual(data['text']['upperback']['textvalue'], "SEOUL NAT'L")
        self.assertEqual(data['text']['upperback']['fontFamily'], "arial")
        self.assertEqual(data['text']['upperback']['fill'], "#ffc107")
        self.assertEqual(data['text']['upperback']['fontStyle'], "bold")
        self.assertEqual(data['text']['upperback']['fontSize'], 25)
        self.assertEqual(data['text']['upperback']['left'], 135)
        self.assertEqual(data['text']['upperback']['top'], 125)
        self.assertEqual(data['text']['upperback']['stroke'], "")
        self.assertEqual(data['text']['upperback']['strokeWidth'], 0)
        self.assertEqual(data['text']['middleback']['textvalue'], "UNIVERSITY")
        self.assertEqual(data['text']['middleback']['fontFamily'], "arial")
        self.assertEqual(data['text']['middleback']['fill'], "#ffc107")
        self.assertEqual(data['text']['middleback']['fontStyle'], "bold")
        self.assertEqual(data['text']['middleback']['fontSize'], 20)
        self.assertEqual(data['text']['middleback']['left'], 155)
        self.assertEqual(data['text']['middleback']['top'], 155)
        self.assertEqual(data['text']['middleback']['stroke'], "")
        self.assertEqual(data['text']['middleback']['strokeWidth'], 0)
        self.assertEqual(data['text']['lowerback']['textvalue'], "Department of\nComputer Science")
        self.assertEqual(data['text']['lowerback']['fontFamily'], "arial")
        self.assertEqual(data['text']['lowerback']['fill'], "#ffc107")
        self.assertEqual(data['text']['lowerback']['fontStyle'], "italic")
        self.assertEqual(data['text']['lowerback']['fontSize'], 15)
        self.assertEqual(data['text']['lowerback']['left'], 151)
        self.assertEqual(data['text']['lowerback']['top'], 256)
        self.assertEqual(data['text']['lowerback']['stroke'], "")
        self.assertEqual(data['text']['lowerback']['strokeWidth'], 0)
        self.assertEqual(data['logo']['front']['src'], DEFAULT_LOGO_BASE64)
        self.assertEqual(data['logo']['front']['width'], 571)
        self.assertEqual(data['logo']['front']['height'], 589)
        self.assertEqual(data['logo']['front']['left'], 357)
        self.assertEqual(data['logo']['front']['top'], 152)
        self.assertEqual(data['logo']['front']['scaleX'], 1)
        self.assertEqual(data['logo']['front']['scaleY'], 1)
        self.assertEqual(data['logo']['back']['src'], DEFAULT_LOGO_BASE64)
        self.assertEqual(data['logo']['back']['width'], 571)
        self.assertEqual(data['logo']['back']['height'], 589)
        self.assertEqual(data['logo']['back']['left'], 212)
        self.assertEqual(data['logo']['back']['top'], 216)
        self.assertEqual(data['logo']['back']['scaleX'], 1)
        self.assertEqual(data['logo']['back']['scaleY'], 1)
        self.assertEqual(data['image']['frontImg'], DEFAULT_IMG_FRONT_URL)
        self.assertEqual(data['image']['backImg'], DEFAULT_IMG_BACK_URL)
        self.assertEqual(data['likes'], 0)
        # id, group, owner should not be null for authorized requests
        self.assertEquals(Group.objects.get(id=data['group']).group_name, 'user_group_newdesign')
        # these ids should be null for unsaved designs
        self.assertEqual(data['text']['frontchest']['id'], None)
        self.assertEqual(data['text']['rightarm']['id'], None)
        self.assertEqual(data['text']['upperback']['id'], None)
        self.assertEqual(data['text']['middleback']['id'], None)
        self.assertEqual(data['text']['lowerback']['id'], None)
        self.assertEqual(data['logo']['front']['id'], None)
        self.assertEqual(data['logo']['back']['id'], None)
        # this design should be set to recent
        user = User.objects.get(username='newdesign')
        profile = Profile.objects.get(user=user)
        self.assertEqual(profile.recent.id, new_design_id)


## Edit Design
class EditDesignCase(TestCase):
    def setUp(self):
        self.client.post('/users/', {'username': 'edit', 'password': 'pass'})
        self.client.post('/users/', {'username': 'unauth', 'password': 'pass'})
        self.client.login(username='edit',password='pass')
        response = self.client.get('/')
        response.render()
        stream = io.BytesIO(response.content)
        data = JSONParser().parse(stream)
        self.design1_id = data['id']
        response = self.client.delete('/')
        response.render()
        stream = io.BytesIO(response.content)
        data = JSONParser().parse(stream)
        self.design2_id = data['id']
    
    # Edit Design
    def test_edit_design(self):
        self.client.logout()
        self.client.login(username='edit',password='pass')
        response = self.client.get('/')
        response.render()
        stream = io.BytesIO(response.content)
        data = JSONParser().parse(stream)
        curr_design_id = data['id']
        self.assertEqual(self.design2_id, curr_design_id)
        user = User.objects.get(username='edit')
        profile = Profile.objects.get(user=user)
        self.assertEqual(profile.recent.id, self.design2_id)
        response = self.client.get('/groups/edit/'+str(self.design1_id)+'/')
        self.assertEqual(response.status_code//100, 2)
        response = self.client.get('/')
        response.render()
        stream = io.BytesIO(response.content)
        data = JSONParser().parse(stream)
        edit_design_id = data['id']
        self.assertFalse(edit_design_id == curr_design_id)
        self.assertEqual(self.design1_id, edit_design_id)
        # edit design should be set to recent
        user = User.objects.get(username='edit')
        profile = Profile.objects.get(user=user)
        self.assertEqual(profile.recent.id, edit_design_id)


    # Non-Owner Edit Design
    def test_without_auth(self):
        # Without Login
        self.client.logout()
        response = self.client.get('/groups/edit/'+str(self.design1_id)+'/')
        self.assertEqual(response.status_code//100, 4)
        # Non-Owner
        self.client.login(username='unauth',password='pass')
        response = self.client.get('/groups/edit/'+str(self.design1_id)+'/')
        self.assertEqual(response.status_code//100, 4)

##########################################################
#################### Test Group Page #####################
##########################################################

## Group Create
class CreateGroupCase(TestCase):
    def setUp(self):
        self.client.post('/users/', {'username': 'creategroup', 'password': 'pass'})

    # Group Create without Login
    def test_without_auth(self):
        self.client.logout()
        try:
            group = Group.objects.get(group_name='unauth_group')
            self.assertEqual(1, 2)
        except Group.DoesNotExist:
            pass
        response = self.client.post('/create_group/', "{\"grouptype\": \"MJ\", \"groupname\": \"unauth_group\"}", content_type='application/json')
        self.assertEqual(response.status_code//100, 4)

    # Group Create
    def test_group_create(self):
        self.client.login(username='creategroup',password='pass')
        try:
            group = Group.objects.get(group_name='new_group')
            self.assertEqual(1, 2)
        except Group.DoesNotExist:
            pass
        response = self.client.post('/create_group/', "{\"grouptype\": \"MJ\", \"groupname\": \"new_group\"}", content_type='application/json')
        self.assertEqual(response.status_code//100, 2)
        try:
            group = Group.objects.get(group_name='new_group')
        except Group.DoesNotExist:
            self.assertEqual(1, 2)
        
        user = User.objects.get(username='creategroup')
        self.assertTrue(user in group.users.all())
        self.assertTrue(user in group.master.all())

    # Group Create with Duplicates
    def test_with_dups(self):
        self.client.login(username='creategroup',password='pass')
        try:
            group = Group.objects.get(group_name='dup_group')
            self.assertEqual(1, 2)
        except Group.DoesNotExist:
            pass
        response = self.client.post('/create_group/', "{\"grouptype\": \"MJ\", \"groupname\": \"dup_group\"}", content_type='application/json')
        try:
            group = Group.objects.get(group_name='dup_group')
        except Group.DoesNotExist:
            self.assertEqual(1, 2)
        response = self.client.post('/create_group/', "{\"grouptype\": \"MJ\", \"groupname\": \"dup_group\"}", content_type='application/json')
        self.assertEqual(response.status_code//100, 4)

    # User Group Create
    def test_user_group(self):
        self.client.login(username='creategroup',password='pass')
        try:
            group = Group.objects.get(group_name='user_group')
            self.assertEqual(1, 2)
        except Group.DoesNotExist:
            pass
        response = self.client.post('/create_group/', "{\"grouptype\": \"UR\", \"groupname\": \"user_group\"}", content_type='application/json')
        self.assertEqual(response.status_code//100, 4)

## Group List
class GroupListCase(TestCase):
    def setUp(self):
        self.client.post('/users/', {'username': 'grouplist1', 'password': 'pass'})
        self.client.login(username='grouplist1',password='pass')
        self.client.post('/create_group/', "{\"grouptype\": \"MJ\", \"groupname\": \"group1\"}", content_type='application/json')
        self.client.post('/create_group/', "{\"grouptype\": \"MJ\", \"groupname\": \"group2\"}", content_type='application/json')
        self.client.logout()
        self.client.post('/users/', {'username': 'grouplist2', 'password': 'pass'})
        self.client.login(username='grouplist2',password='pass')
        self.client.post('/create_group/', "{\"grouptype\": \"MJ\", \"groupname\": \"group3\"}", content_type='application/json')
        self.client.post('/create_group/', "{\"grouptype\": \"MJ\", \"groupname\": \"group4\"}", content_type='application/json')
        self.client.logout()
        self.groups = Group.objects.all().exclude(group_type='UR')

    # Get Whole Group List
    def test_whole_group(self):
        self.client.logout()
        response = self.client.get('/groups/')
        self.assertEqual(response.status_code//100, 2)
        response.render()
        stream = io.BytesIO(response.content)
        data = JSONParser().parse(stream)
        response_groups = []
        for group in data:
            try:
                response_groups.append(Group.objects.get(id=group['id']))
            except Group.DoesNotExist:
                self.assertEqual(1, 2)
        for group in self.groups:
            self.assertTrue(group in response_groups)
        
    # Get Joined Group List
    def test_joined_group(self):
        user = User.objects.get(username='grouplist1')
        self.client.login(username='grouplist1',password='pass')
        groups = Group.objects.all()
        response = self.client.get('/groups/grouplist1/')
        self.assertEqual(response.status_code//100, 2)
        response.render()
        stream = io.BytesIO(response.content)
        data = JSONParser().parse(stream)
        response_groups = []
        for group in data:
            try:
                response_groups.append(Group.objects.get(id=group['id']))
            except Group.DoesNotExist:
                self.assertEqual(1, 2)
        for group in groups:
            if user in group.users.all():
                self.assertTrue(group in response_groups)

    # Get Joined Group List without Login
    def test_without_auth(self):
        self.client.logout()
        response = self.client.get('/groups/grouplist1/')
        self.assertEqual(response.status_code//100, 4)

## Group Join
class GroupJoinCase(TestCase):
    def setUp(self):
        self.client.post('/users/', {'username': 'groupjoin1', 'password': 'pass'})
        self.client.post('/users/', {'username': 'groupjoin2', 'password': 'pass'})
        self.client.login(username='groupjoin1',password='pass')
        self.client.post('/create_group/', "{\"grouptype\": \"MJ\", \"groupname\": \"dest_group\"}", content_type='application/json')
        self.client.logout()
        self.group = Group.objects.get(group_name='dest_group')

    
    # Group Join without Login
    def test_without_auth(self):
        self.client.logout()
        response = self.client.get('/join_group/' + str(self.group.id) + '/')
        self.assertEqual(response.status_code//100, 4)

    # Group Join
    def test_group_join(self):
        user = User.objects.get(username='groupjoin2')
        self.assertTrue(user not in self.group.users.all())
        self.client.login(username='groupjoin2',password='pass')
        response = self.client.get('/join_group/' + str(self.group.id) + '/')
        self.assertEqual(response.status_code//100, 2)
        self.assertTrue(user in self.group.users.all())
        self.client.logout()

    # Join Same Group
    def test_with_dups(self):
        self.client.login(username='groupjoin1',password='pass')
        response = self.client.get('/join_group/' + str(self.group.id) + '/')
        self.assertEqual(response.status_code//100, 4)
        self.client.logout()

    # Join User Group
    def test_user_group(self):
        gid = Group.objects.get(group_name='user_group_groupjoin2').id
        self.client.login(username='groupjoin1',password='pass')
        response = self.client.get('/join_group/' + str(gid) + '/')
        self.assertEqual(response.status_code//100, 4)
        self.client.logout()

    # Join UnExisting Group
    def test_unexisting(self):
        gid = 100
        try:
            group = Group.objects.get(id=gid)
            self.assertEqual(1, 2)
        except Group.DoesNotExist:
            pass
        self.client.login(username='groupjoin1',password='pass')
        response = self.client.get('/join_group/' + str(gid) + '/')
        self.assertEqual(response.status_code//100, 4)
        self.client.logout()

## Group Admin
class GroupAdminCase(TestCase):
    def setUp(self):
        self.client.post('/users/', {'username': 'groupadmin1', 'password': 'pass'})
        self.client.post('/users/', {'username': 'groupadmin2', 'password': 'pass'})
        self.client.post('/users/', {'username': 'groupadmin3', 'password': 'pass'})
        self.client.post('/users/', {'username': 'groupadmin4', 'password': 'pass'})
        self.client.login(username='groupadmin1',password='pass')
        self.client.post('/create_group/', "{\"grouptype\": \"MJ\", \"groupname\": \"admin_group\"}", content_type='application/json')
        self.client.post('/create_group/', "{\"grouptype\": \"MJ\", \"groupname\": \"admin_group_dup\"}", content_type='application/json')
        self.client.logout()
        self.group = Group.objects.get(group_name='admin_group')
        self.client.login(username='groupadmin2',password='pass')
        self.client.get('/join_group/' + str(self.group.id) + '/')
        self.client.logout()
        self.client.login(username='groupadmin3',password='pass')
        self.client.get('/join_group/' + str(self.group.id) + '/')
        self.client.logout()
    
    # Access without Login
    # Access without Admin Rights
    def test_without_auth(self):
        self.client.logout()
        response = self.client.get('/groups/' + str(self.group.id) + '/admin/')
        self.assertEqual(response.status_code//100, 4)
        self.client.login(username='groupadmin2',password='pass')
        response = self.client.get('/groups/' + str(self.group.id) + '/admin/')
        self.assertEqual(response.status_code//100, 2)
        self.client.logout()
        self.client.login(username='groupadmin4',password='pass')
        response = self.client.get('/groups/' + str(self.group.id) + '/admin/')
        self.assertEqual(response.status_code//100, 4)
        self.client.logout()
        
    # Access UnExisting Group Admin
    def test_unexisting(self):
        gid = 100
        try:
            group = Group.objects.get(id=gid)
            self.assertEqual(1, 2)
        except Group.DoesNotExist:
            pass
        self.client.login(username='groupadmin4',password='pass')
        response = self.client.get('/groups/' + str(gid) + '/admin/')
        self.assertEqual(response.status_code//100, 4)
        self.client.logout()

    # Group Type Change
    # Group Name Change
    def test_group_change(self):
        self.client.login(username='groupadmin1',password='pass')
        response = self.client.get('/groups/' + str(self.group.id) + '/admin/')
        response.render()
        stream = io.BytesIO(response.content)
        data = JSONParser().parse(stream)
        self.assertEqual(data[0]['group_name'], 'admin_group')
        self.assertEqual(data[0]['group_type'], 'MJ')
        response = self.client.put('/groups/' + str(self.group.id) + '/admin/', """{
            \"group_name\": \"hello_world\",
            \"group_type\": \"CL\"
            }""",
            content_type='application/json')
        self.assertEqual(response.status_code//100, 2)
        response = self.client.get('/groups/' + str(self.group.id) + '/admin/')
        response.render()
        stream = io.BytesIO(response.content)
        data = JSONParser().parse(stream)
        self.assertFalse(data[0]['group_name'] == 'admin_group')
        self.assertFalse(data[0]['group_type'] == 'MJ')
        self.assertEqual(data[0]['group_name'], 'hello_world')
        self.assertEqual(data[0]['group_type'], 'CL')
        self.assertEqual(self.group.id, data[0]['id'])
        self.client.logout()

    # Group Name Change with Duplicates
    def test_with_dups(self):
        self.client.login(username='groupadmin1',password='pass')
        response = self.client.put('/groups/' + str(self.group.id) + '/admin/', """{
            \"group_name\": \"admin_group_dup\",
            \"group_type\": \"MJ\"
            }""",
            content_type='application/json')
        self.assertEqual(response.status_code//100, 4)
        

    # Member to Admin
    # Member Drop
    # Drop Admin
    # Drop Self
    def test_update_member(self):
        user1 = User.objects.get(username='groupadmin1')
        user2 = User.objects.get(username='groupadmin2')
        user3 = User.objects.get(username='groupadmin3')
        
        # Member to Admin
        self.assertTrue(user2 not in self.group.master.all())
        self.client.login(username='groupadmin1',password='pass')
        response = self.client.put('/groups/' + str(self.group.id) + '/members/' + str(user2.id) + '/')
        self.assertEqual(response.status_code//100, 2)
        self.assertTrue(user2 in self.group.master.all())

        # Member Drop
        self.assertTrue(user3 in self.group.users.all())
        response = self.client.delete('/groups/' + str(self.group.id) + '/members/' + str(user3.id) + '/')
        self.assertEqual(response.status_code//100, 2)
        self.assertTrue(user3 not in self.group.master.all())

        # Drop Self
        response = self.client.delete('/groups/' + str(self.group.id) + '/members/' + str(user1.id) + '/')
        self.assertEqual(response.status_code//100, 4)

        # Drop Admin
        self.assertTrue(user2 in self.group.master.all())
        self.assertTrue(user2 in self.group.users.all())
        response = self.client.delete('/groups/' + str(self.group.id) + '/members/' + str(user2.id) + '/')
        self.assertEqual(response.status_code//100, 2)
        self.assertTrue(user2 not in self.group.master.all())
        self.assertTrue(user2 not in self.group.users.all())
        self.client.logout()

## Group Drop
class GroupDropCase(TestCase):
    def setUp(self):
        self.client.post('/users/', {'username': 'groupdrop1', 'password': 'pass'})
        self.client.post('/users/', {'username': 'groupdrop2', 'password': 'pass'})
        self.client.post('/users/', {'username': 'groupdrop3', 'password': 'pass'})
        self.client.post('/users/', {'username': 'groupdrop4', 'password': 'pass'})
        self.client.login(username='groupdrop1',password='pass')
        self.client.post('/create_group/', "{\"grouptype\": \"MJ\", \"groupname\": \"drop_group\"}", content_type='application/json')
        self.client.logout()
        self.group = Group.objects.get(group_name='drop_group')
        self.client.login(username='groupdrop2',password='pass')
        self.client.get('/join_group/' + str(self.group.id) + '/')
        self.client.logout()
        self.client.login(username='groupdrop3',password='pass')
        self.client.get('/join_group/' + str(self.group.id) + '/')
        self.client.logout()

    # Member Group Drop
    def test_group_drop(self):
        user = User.objects.get(username='groupdrop3')
        self.assertTrue(user in self.group.users.all())
        self.client.login(username='groupdrop3',password='pass')
        response = self.client.get('/groups/' + str(self.group.id) + '/drop/')
        self.assertEqual(response.status_code//100, 2)
        self.assertTrue(user not in self.group.users.all())
        self.client.logout()

    # Member Drop Group not Joined
    # Drop UnExisting Group
    def test_unexisting(self):
        user = User.objects.get(username='groupdrop4')
        self.assertTrue(user not in self.group.users.all())
        self.client.login(username='groupdrop4',password='pass')
        response = self.client.get('/groups/' + str(self.group.id) + '/drop/')
        self.assertEqual(response.status_code//100, 4)
        gid = 100
        try:
            group = Group.objects.get(id=gid)
            self.assertEqual(1, 2)
        except Group.DoesNotExist:
            pass
        response = self.client.get('/groups/' + str(gid) + '/drop/')
        self.assertEqual(response.status_code//100, 4)
        self.client.logout()

    # Admin Drop
    # Last Admin Drop
    def test_admin_drop(self):
        user1 = User.objects.get(username='groupdrop1')
        user2 = User.objects.get(username='groupdrop2')
        self.client.login(username='groupdrop1',password='pass')
        self.client.put('/groups/' + str(self.group.id) + '/members/' + str(user2.id) + '/')
        self.assertTrue(user1 in self.group.master.all())
        self.assertTrue(user1 in self.group.users.all())
        response = self.client.get('/groups/' + str(self.group.id) + '/drop/')
        self.assertEqual(response.status_code//100, 2)
        self.assertTrue(user1 not in self.group.master.all())
        self.assertTrue(user1 not in self.group.users.all())
        self.client.logout()
        self.client.login(username='groupdrop2',password='pass')
        self.assertTrue(user2 in self.group.master.all())
        self.assertTrue(user2 in self.group.users.all())
        response = self.client.get('/groups/' + str(self.group.id) + '/drop/')
        self.assertEqual(response.status_code//100, 4)
        self.client.logout()

    # Drop User Group
    def test_user_group(self):
        gid = Group.objects.get(group_name='user_group_groupdrop1').id
        self.client.login(username='groupdrop1',password='pass')
        response = self.client.get('/groups/' + str(gid) + '/drop/')
        self.assertEqual(response.status_code//100, 4)

## Post Design
class PostDesignCase(TestCase):
    def setUp(self):
        self.client.post('/users/', {'username': 'post1', 'password': 'pass'})
        self.client.post('/users/', {'username': 'post2', 'password': 'pass'})
        self.client.login(username='post1',password='pass')
        response = self.client.get('/')
        response.render()
        stream = io.BytesIO(response.content)
        data = JSONParser().parse(stream)
        self.design_id1 = data['id']
        design_data = """{
            \"id\": """ + str(self.design_id1) + """,
            \"design\": {
                \"body\": \"#fcfcfc\",
                \"button\": \"#fcfcfc\",
                \"sleeve\": \"#fcfcfc\",
                \"banding\": \"#fcfcfc\",
                \"stripe\": \"#fcfcfc\"
            },
            \"text\": {
                \"frontchest\": {
                    \"id\": null,
                    \"textvalue\": \"S\",
                    \"fontFamily\": \"arial\",
                    \"fill\": \"#3f51b5\",
                    \"fontStyle\": \"bold\",
                    \"fontSize\": 50,
                    \"left\": 250,
                    \"top\": 110,
                    \"stroke\": \"#000000\",
                    \"strokeWidth\": 2
                },
                \"rightarm\": {
                    \"id\": null,
                    \"textvalue\": \"19\",
                    \"fontFamily\": \"arial\",
                    \"fill\": \"#607d8b\",
                    \"fontStyle\": \"bold\",
                    \"fontSize\": 50,
                    \"left\": 50,
                    \"top\": 120,
                    \"stroke\": \"\",
                    \"strokeWidth\": 0
                },
                \"upperback\": {
                    \"id\": null,
                    \"textvalue\": \"SEOUL NAT'L\",
                    \"fontFamily\": \"arial\",
                    \"fill\": \"#ffc107\",
                    \"fontStyle\": \"bold\",
                    \"fontSize\": 25,
                    \"left\": 135,
                    \"top\": 125,
                    \"stroke\": \"\",
                    \"strokeWidth\": 0
                },
                \"middleback\": {
                    \"id\": null,
                    \"textvalue\": \"UNIVERSITY\",
                    \"fontFamily\": \"arial\",
                    \"fill\": \"#ffc107\",
                    \"fontStyle\": \"bold\",
                    \"fontSize\": 20,
                    \"left\": 155,
                    \"top\": 155,
                    \"stroke\": \"\",
                    \"strokeWidth\": 0
                },
                \"lowerback\": {
                    \"id\": null,
                    \"textvalue\": \"hi\",
                    \"fontFamily\": \"arial\",
                    \"fill\": \"#ffc107\",
                    \"fontStyle\": \"bold\",
                    \"fontSize\": 15,
                    \"left\": 150,
                    \"top\": 190,
                    \"stroke\": \"\",
                    \"strokeWidth\": 0
                }
            },
            \"logo\": {
                \"front\": {
                    \"id\": null,
                    \"src\": \"hi\",
                    \"width\": 571,
                    \"height\": 589,
                    \"left\": 340,
                    \"top\": 180,
                    \"scaleX\": 1,
                    \"scaleY\": 1
                },
                \"back\": {
                    \"id\": null,
                    \"src\": \"hi\",
                    \"width\": 571,
                    \"height\": 589,
                    \"left\": 215,
                    \"top\": 280,
                    \"scaleX\": 1,
                    \"scaleY\": 1
                }
            },
            \"image\": {
                \"frontImg\": null,
                \"backImg\": null
            }
        }"""
        self.client.put(path='/', data=design_data, content_type='application/json')
        self.client.post('/create_group/', "{\"grouptype\": \"MJ\", \"groupname\": \"post_group\"}", content_type='application/json')
        self.client.logout()
        self.client.login(username='post2',password='pass')
        response = self.client.get('/')
        response.render()
        stream = io.BytesIO(response.content)
        data = JSONParser().parse(stream)
        self.design_id2 = data['id']
        design_data = """{
            \"id\": """ + str(self.design_id2) + """,
            \"design\": {
                \"body\": \"#fcfcfc\",
                \"button\": \"#fcfcfc\",
                \"sleeve\": \"#fcfcfc\",
                \"banding\": \"#fcfcfc\",
                \"stripe\": \"#fcfcfc\"
            },
            \"text\": {
                \"frontchest\": {
                    \"id\": null,
                    \"textvalue\": \"S\",
                    \"fontFamily\": \"arial\",
                    \"fill\": \"#3f51b5\",
                    \"fontStyle\": \"bold\",
                    \"fontSize\": 50,
                    \"left\": 250,
                    \"top\": 110,
                    \"stroke\": \"#000000\",
                    \"strokeWidth\": 2
                },
                \"rightarm\": {
                    \"id\": null,
                    \"textvalue\": \"19\",
                    \"fontFamily\": \"arial\",
                    \"fill\": \"#607d8b\",
                    \"fontStyle\": \"bold\",
                    \"fontSize\": 50,
                    \"left\": 50,
                    \"top\": 120,
                    \"stroke\": \"\",
                    \"strokeWidth\": 0
                },
                \"upperback\": {
                    \"id\": null,
                    \"textvalue\": \"SEOUL NAT'L\",
                    \"fontFamily\": \"arial\",
                    \"fill\": \"#ffc107\",
                    \"fontStyle\": \"bold\",
                    \"fontSize\": 25,
                    \"left\": 135,
                    \"top\": 125,
                    \"stroke\": \"\",
                    \"strokeWidth\": 0
                },
                \"middleback\": {
                    \"id\": null,
                    \"textvalue\": \"UNIVERSITY\",
                    \"fontFamily\": \"arial\",
                    \"fill\": \"#ffc107\",
                    \"fontStyle\": \"bold\",
                    \"fontSize\": 20,
                    \"left\": 155,
                    \"top\": 155,
                    \"stroke\": \"\",
                    \"strokeWidth\": 0
                },
                \"lowerback\": {
                    \"id\": null,
                    \"textvalue\": \"hi\",
                    \"fontFamily\": \"arial\",
                    \"fill\": \"#ffc107\",
                    \"fontStyle\": \"bold\",
                    \"fontSize\": 15,
                    \"left\": 150,
                    \"top\": 190,
                    \"stroke\": \"\",
                    \"strokeWidth\": 0
                }
            },
            \"logo\": {
                \"front\": {
                    \"id\": null,
                    \"src\": \"hi\",
                    \"width\": 571,
                    \"height\": 589,
                    \"left\": 340,
                    \"top\": 180,
                    \"scaleX\": 1,
                    \"scaleY\": 1
                },
                \"back\": {
                    \"id\": null,
                    \"src\": \"hi\",
                    \"width\": 571,
                    \"height\": 589,
                    \"left\": 215,
                    \"top\": 280,
                    \"scaleX\": 1,
                    \"scaleY\": 1
                }
            },
            \"image\": {
                \"frontImg\": null,
                \"backImg\": null
            }
        }"""
        self.client.put(path='/', data=design_data, content_type='application/json')
        self.client.logout()
        self.group = Group.objects.get(group_name='post_group')

    # Post Design without Login
    # Post Design to Group not Joined
    def test_without_auth(self):
        self.client.logout()
        response = self.client.get('/groups/'+str(self.group.id)+'/post/'+str(self.design_id1)+'/')
        self.assertEqual(response.status_code//100, 4)
        self.client.login(username='post2',password='pass')
        response = self.client.get('/groups/'+str(self.group.id)+'/post/'+str(self.design_id2)+'/')
        self.assertEqual(response.status_code//100, 4)
        self.client.logout()
    
    # Post Design
    def test_post_design(self):
        self.client.login(username='post1',password='pass')
        response = self.client.get('/groups/'+str(self.group.id)+'/post/'+str(self.design_id1)+'/')
        self.assertEqual(response.status_code//100, 2)
        response.render()
        stream = io.BytesIO(response.content)
        data = JSONParser().parse(stream)
        self.assertEqual(data['group'], self.group.id)
        design = Design.objects.get(id=data['id'])
        self.assertEquals(design.group, self.group)
        self.client.logout()

    # Post UnExisting Design
    # Post Design to UnExisting Group
    def test_unexisting(self):
        self.client.login(username='post1',password='pass')
        did = 100
        try:
            design = Design.objects.get(id=did)
            self.assertEqual(1, 2)
        except Design.DoesNotExist:
            pass
        response = self.client.get('/groups/'+str(self.group.id)+'/post/'+str(did)+'/')
        self.assertEqual(response.status_code//100, 4)
        gid = 100
        try:
            group = Group.objects.get(id=gid)
            self.assertEqual(1, 2)
        except Group.DoesNotExist:
            pass
        response = self.client.get('/groups/'+str(gid)+'/post/'+str(self.design_id1)+'/')
        self.assertEqual(response.status_code//100, 4)

## Group Detail
class GroupDetailCase(TestCase):
    def setUp(self):
        self.client.post('/users/', {'username': 'detail1', 'password': 'pass'})
        self.client.post('/users/', {'username': 'detail2', 'password': 'pass'})
        self.client.login(username='detail1',password='pass')
        self.client.post('/create_group/', "{\"grouptype\": \"MJ\", \"groupname\": \"detail_group\"}", content_type='application/json')
        self.group = Group.objects.get(group_name='detail_group')
        response = self.client.get('/')
        response.render()
        stream = io.BytesIO(response.content)
        data = JSONParser().parse(stream)
        design_id1 = data['id']
        design_data = """{
            \"id\": """ + str(design_id1) + """,
            \"design\": {
                \"body\": \"#fcfcfc\",
                \"button\": \"#fcfcfc\",
                \"sleeve\": \"#fcfcfc\",
                \"banding\": \"#fcfcfc\",
                \"stripe\": \"#fcfcfc\"
            },
            \"text\": {
                \"frontchest\": {
                    \"id\": null,
                    \"textvalue\": \"S\",
                    \"fontFamily\": \"arial\",
                    \"fill\": \"#3f51b5\",
                    \"fontStyle\": \"bold\",
                    \"fontSize\": 50,
                    \"left\": 250,
                    \"top\": 110,
                    \"stroke\": \"#000000\",
                    \"strokeWidth\": 2
                },
                \"rightarm\": {
                    \"id\": null,
                    \"textvalue\": \"19\",
                    \"fontFamily\": \"arial\",
                    \"fill\": \"#607d8b\",
                    \"fontStyle\": \"bold\",
                    \"fontSize\": 50,
                    \"left\": 50,
                    \"top\": 120,
                    \"stroke\": \"\",
                    \"strokeWidth\": 0
                },
                \"upperback\": {
                    \"id\": null,
                    \"textvalue\": \"SEOUL NAT'L\",
                    \"fontFamily\": \"arial\",
                    \"fill\": \"#ffc107\",
                    \"fontStyle\": \"bold\",
                    \"fontSize\": 25,
                    \"left\": 135,
                    \"top\": 125,
                    \"stroke\": \"\",
                    \"strokeWidth\": 0
                },
                \"middleback\": {
                    \"id\": null,
                    \"textvalue\": \"UNIVERSITY\",
                    \"fontFamily\": \"arial\",
                    \"fill\": \"#ffc107\",
                    \"fontStyle\": \"bold\",
                    \"fontSize\": 20,
                    \"left\": 155,
                    \"top\": 155,
                    \"stroke\": \"\",
                    \"strokeWidth\": 0
                },
                \"lowerback\": {
                    \"id\": null,
                    \"textvalue\": \"hi\",
                    \"fontFamily\": \"arial\",
                    \"fill\": \"#ffc107\",
                    \"fontStyle\": \"bold\",
                    \"fontSize\": 15,
                    \"left\": 150,
                    \"top\": 190,
                    \"stroke\": \"\",
                    \"strokeWidth\": 0
                }
            },
            \"logo\": {
                \"front\": {
                    \"id\": null,
                    \"src\": \"hi\",
                    \"width\": 571,
                    \"height\": 589,
                    \"left\": 340,
                    \"top\": 180,
                    \"scaleX\": 1,
                    \"scaleY\": 1
                },
                \"back\": {
                    \"id\": null,
                    \"src\": \"hi\",
                    \"width\": 571,
                    \"height\": 589,
                    \"left\": 215,
                    \"top\": 280,
                    \"scaleX\": 1,
                    \"scaleY\": 1
                }
            },
            \"image\": {
                \"frontImg\": null,
                \"backImg\": null
            }
        }"""
        self.client.put(path='/', data=design_data, content_type='application/json')
        response = self.client.get('/groups/'+str(self.group.id)+'/post/'+str(design_id1)+'/')
        response.render()
        stream = io.BytesIO(response.content)
        data = JSONParser().parse(stream)
        self.group_design_id1 = data['id']
        response = self.client.delete('/')
        response.render()
        stream = io.BytesIO(response.content)
        data = JSONParser().parse(stream)
        design_id2 = data['id']
        design_data = """{
            \"id\": """ + str(design_id2) + """,
            \"design\": {
                \"body\": \"#fcfcfc\",
                \"button\": \"#fcfcfc\",
                \"sleeve\": \"#fcfcfc\",
                \"banding\": \"#fcfcfc\",
                \"stripe\": \"#fcfcfc\"
            },
            \"text\": {
                \"frontchest\": {
                    \"id\": null,
                    \"textvalue\": \"S\",
                    \"fontFamily\": \"arial\",
                    \"fill\": \"#3f51b5\",
                    \"fontStyle\": \"bold\",
                    \"fontSize\": 50,
                    \"left\": 250,
                    \"top\": 110,
                    \"stroke\": \"#000000\",
                    \"strokeWidth\": 2
                },
                \"rightarm\": {
                    \"id\": null,
                    \"textvalue\": \"19\",
                    \"fontFamily\": \"arial\",
                    \"fill\": \"#607d8b\",
                    \"fontStyle\": \"bold\",
                    \"fontSize\": 50,
                    \"left\": 50,
                    \"top\": 120,
                    \"stroke\": \"\",
                    \"strokeWidth\": 0
                },
                \"upperback\": {
                    \"id\": null,
                    \"textvalue\": \"SEOUL NAT'L\",
                    \"fontFamily\": \"arial\",
                    \"fill\": \"#ffc107\",
                    \"fontStyle\": \"bold\",
                    \"fontSize\": 25,
                    \"left\": 135,
                    \"top\": 125,
                    \"stroke\": \"\",
                    \"strokeWidth\": 0
                },
                \"middleback\": {
                    \"id\": null,
                    \"textvalue\": \"UNIVERSITY\",
                    \"fontFamily\": \"arial\",
                    \"fill\": \"#ffc107\",
                    \"fontStyle\": \"bold\",
                    \"fontSize\": 20,
                    \"left\": 155,
                    \"top\": 155,
                    \"stroke\": \"\",
                    \"strokeWidth\": 0
                },
                \"lowerback\": {
                    \"id\": null,
                    \"textvalue\": \"hi\",
                    \"fontFamily\": \"arial\",
                    \"fill\": \"#ffc107\",
                    \"fontStyle\": \"bold\",
                    \"fontSize\": 15,
                    \"left\": 150,
                    \"top\": 190,
                    \"stroke\": \"\",
                    \"strokeWidth\": 0
                }
            },
            \"logo\": {
                \"front\": {
                    \"id\": null,
                    \"src\": \"hi\",
                    \"width\": 571,
                    \"height\": 589,
                    \"left\": 340,
                    \"top\": 180,
                    \"scaleX\": 1,
                    \"scaleY\": 1
                },
                \"back\": {
                    \"id\": null,
                    \"src\": \"hi\",
                    \"width\": 571,
                    \"height\": 589,
                    \"left\": 215,
                    \"top\": 280,
                    \"scaleX\": 1,
                    \"scaleY\": 1
                }
            },
            \"image\": {
                \"frontImg\": null,
                \"backImg\": null
            }
        }"""
        self.client.put(path='/', data=design_data, content_type='application/json')
        response = self.client.get('/groups/'+str(self.group.id)+'/post/'+str(design_id2)+'/')
        response.render()
        stream = io.BytesIO(response.content)
        data = JSONParser().parse(stream)
        self.group_design_id2 = data['id']
        self.client.logout()

    # Get Design without Login
    # Get Designs of Group not Joined
    def test_without_auth(self):
        self.client.logout()
        response = self.client.get('groups/'+str(self.group.id)+'/')
        self.assertEqual(response.status_code//100, 4)
            
    # Get Designs
    def test_group_detail(self):
        self.client.login(username='detail1',password='pass')
        response = self.client.get('/groups/'+str(self.group.id)+'/')
        self.assertEqual(response.status_code//100, 2)
        response.render()
        stream = io.BytesIO(response.content)
        data = JSONParser().parse(stream)
        response_designs = []
        for design in data:
            try:
                response_designs.append(Design.objects.get(id=design['id']))
            except Design.DoesNotExist:
                self.assertEqual(1, 2)
        for design in Design.objects.all().filter(group=self.group):
            self.assertTrue(design in response_designs)
        self.client.logout()

        self.client.login(username='detail2',password='pass')
        response = self.client.get('/groups/'+str(self.group.id)+'/')
        self.assertEqual(response.status_code//100, 4)

    # Get Designs of UnExisting Group
    def test_unexisting(self):
        self.client.login(username='detail1',password='pass')
        gid = 100
        try:
            group = Group.objects.get(id=gid)
            self.assertEqual(1, 2)
        except Group.DoesNotExist:
            pass
        response = self.client.get('/groups/'+str(gid)+'/')
        self.assertEqual(response.status_code//100, 4)

## Delete Design
class DeleteDesignCase(TestCase):
    def setUp(self):
        self.client.post('/users/', {'username': 'delete1', 'password': 'pass'})
        self.client.post('/users/', {'username': 'delete2', 'password': 'pass'})
        self.client.login(username='delete1',password='pass')
        self.client.post('/create_group/', "{\"grouptype\": \"MJ\", \"groupname\": \"delete_group\"}", content_type='application/json')
        self.group = Group.objects.get(group_name='delete_group')
        response = self.client.get('/')
        response.render()
        stream = io.BytesIO(response.content)
        data = JSONParser().parse(stream)
        design_id1 = data['id']
        design_data = """{
            \"id\": """ + str(design_id1) + """,
            \"design\": {
                \"body\": \"#fcfcfc\",
                \"button\": \"#fcfcfc\",
                \"sleeve\": \"#fcfcfc\",
                \"banding\": \"#fcfcfc\",
                \"stripe\": \"#fcfcfc\"
            },
            \"text\": {
                \"frontchest\": {
                    \"id\": null,
                    \"textvalue\": \"S\",
                    \"fontFamily\": \"arial\",
                    \"fill\": \"#3f51b5\",
                    \"fontStyle\": \"bold\",
                    \"fontSize\": 50,
                    \"left\": 250,
                    \"top\": 110,
                    \"stroke\": \"#000000\",
                    \"strokeWidth\": 2
                },
                \"rightarm\": {
                    \"id\": null,
                    \"textvalue\": \"19\",
                    \"fontFamily\": \"arial\",
                    \"fill\": \"#607d8b\",
                    \"fontStyle\": \"bold\",
                    \"fontSize\": 50,
                    \"left\": 50,
                    \"top\": 120,
                    \"stroke\": \"\",
                    \"strokeWidth\": 0
                },
                \"upperback\": {
                    \"id\": null,
                    \"textvalue\": \"SEOUL NAT'L\",
                    \"fontFamily\": \"arial\",
                    \"fill\": \"#ffc107\",
                    \"fontStyle\": \"bold\",
                    \"fontSize\": 25,
                    \"left\": 135,
                    \"top\": 125,
                    \"stroke\": \"\",
                    \"strokeWidth\": 0
                },
                \"middleback\": {
                    \"id\": null,
                    \"textvalue\": \"UNIVERSITY\",
                    \"fontFamily\": \"arial\",
                    \"fill\": \"#ffc107\",
                    \"fontStyle\": \"bold\",
                    \"fontSize\": 20,
                    \"left\": 155,
                    \"top\": 155,
                    \"stroke\": \"\",
                    \"strokeWidth\": 0
                },
                \"lowerback\": {
                    \"id\": null,
                    \"textvalue\": \"hi\",
                    \"fontFamily\": \"arial\",
                    \"fill\": \"#ffc107\",
                    \"fontStyle\": \"bold\",
                    \"fontSize\": 15,
                    \"left\": 150,
                    \"top\": 190,
                    \"stroke\": \"\",
                    \"strokeWidth\": 0
                }
            },
            \"logo\": {
                \"front\": {
                    \"id\": null,
                    \"src\": \"hi\",
                    \"width\": 571,
                    \"height\": 589,
                    \"left\": 340,
                    \"top\": 180,
                    \"scaleX\": 1,
                    \"scaleY\": 1
                },
                \"back\": {
                    \"id\": null,
                    \"src\": \"hi\",
                    \"width\": 571,
                    \"height\": 589,
                    \"left\": 215,
                    \"top\": 280,
                    \"scaleX\": 1,
                    \"scaleY\": 1
                }
            },
            \"image\": {
                \"frontImg\": null,
                \"backImg\": null
            }
        }"""
        self.client.put(path='/', data=design_data, content_type='application/json')
        response = self.client.get('/groups/'+str(self.group.id)+'/post/'+str(design_id1)+'/')
        response.render()
        stream = io.BytesIO(response.content)
        data = JSONParser().parse(stream)
        self.group_design_id1 = data['id']
        response = self.client.delete('/')
        response.render()
        stream = io.BytesIO(response.content)
        data = JSONParser().parse(stream)
        design_id2 = data['id']
        design_data = """{
            \"id\": """ + str(design_id2) + """,
            \"design\": {
                \"body\": \"#fcfcfc\",
                \"button\": \"#fcfcfc\",
                \"sleeve\": \"#fcfcfc\",
                \"banding\": \"#fcfcfc\",
                \"stripe\": \"#fcfcfc\"
            },
            \"text\": {
                \"frontchest\": {
                    \"id\": null,
                    \"textvalue\": \"S\",
                    \"fontFamily\": \"arial\",
                    \"fill\": \"#3f51b5\",
                    \"fontStyle\": \"bold\",
                    \"fontSize\": 50,
                    \"left\": 250,
                    \"top\": 110,
                    \"stroke\": \"#000000\",
                    \"strokeWidth\": 2
                },
                \"rightarm\": {
                    \"id\": null,
                    \"textvalue\": \"19\",
                    \"fontFamily\": \"arial\",
                    \"fill\": \"#607d8b\",
                    \"fontStyle\": \"bold\",
                    \"fontSize\": 50,
                    \"left\": 50,
                    \"top\": 120,
                    \"stroke\": \"\",
                    \"strokeWidth\": 0
                },
                \"upperback\": {
                    \"id\": null,
                    \"textvalue\": \"SEOUL NAT'L\",
                    \"fontFamily\": \"arial\",
                    \"fill\": \"#ffc107\",
                    \"fontStyle\": \"bold\",
                    \"fontSize\": 25,
                    \"left\": 135,
                    \"top\": 125,
                    \"stroke\": \"\",
                    \"strokeWidth\": 0
                },
                \"middleback\": {
                    \"id\": null,
                    \"textvalue\": \"UNIVERSITY\",
                    \"fontFamily\": \"arial\",
                    \"fill\": \"#ffc107\",
                    \"fontStyle\": \"bold\",
                    \"fontSize\": 20,
                    \"left\": 155,
                    \"top\": 155,
                    \"stroke\": \"\",
                    \"strokeWidth\": 0
                },
                \"lowerback\": {
                    \"id\": null,
                    \"textvalue\": \"hi\",
                    \"fontFamily\": \"arial\",
                    \"fill\": \"#ffc107\",
                    \"fontStyle\": \"bold\",
                    \"fontSize\": 15,
                    \"left\": 150,
                    \"top\": 190,
                    \"stroke\": \"\",
                    \"strokeWidth\": 0
                }
            },
            \"logo\": {
                \"front\": {
                    \"id\": null,
                    \"src\": \"hi\",
                    \"width\": 571,
                    \"height\": 589,
                    \"left\": 340,
                    \"top\": 180,
                    \"scaleX\": 1,
                    \"scaleY\": 1
                },
                \"back\": {
                    \"id\": null,
                    \"src\": \"hi\",
                    \"width\": 571,
                    \"height\": 589,
                    \"left\": 215,
                    \"top\": 280,
                    \"scaleX\": 1,
                    \"scaleY\": 1
                }
            },
            \"image\": {
                \"frontImg\": null,
                \"backImg\": null
            }
        }"""
        self.client.put(path='/', data=design_data, content_type='application/json')
        response = self.client.get('/groups/'+str(self.group.id)+'/post/'+str(design_id2)+'/')
        response.render()
        stream = io.BytesIO(response.content)
        data = JSONParser().parse(stream)
        self.group_design_id2 = data['id']
        self.client.logout()
        self.client.login(username='delete2',password='pass')
        self.client.get('/join_group/' + str(self.group.id) + '/')
        self.client.logout()

    # Delete Design without Login
    # Unauthorized Delete
    def test_without_auth(self):
        self.client.logout()
        response = self.client.get('/groups/delete/'+str(self.group_design_id1)+'/')
        self.assertEqual(response.status_code//100, 4)
        self.client.login(username='delete2',password='pass')
        response = self.client.get('/groups/delete/'+str(self.group_design_id2)+'/')
        self.assertEqual(response.status_code//100, 4)
        self.client.logout()

    # Owner Delete Design
    def test_design_delete(self):
        self.client.login(username='delete1',password='pass')
        response = self.client.get('/groups/delete/'+str(self.group_design_id1)+'/')
        self.assertEqual(response.status_code//100, 2)
        self.client.logout()
        try:
            design = Design.objects.get(id=self.group_design_id1)
            self.assertEqual(1, 2)
        except Design.DoesNotExist:
            pass

    
    # Admin Delete Design
    def test_admin(self):
        user = User.objects.get(username='delete2')
        self.client.login(username='delete1',password='pass')
        response = self.client.put('/groups/' + str(self.group.id) + '/members/' + str(user.id) + '/')
        self.client.logout()
        self.client.login(username='delete2',password='pass')
        response = self.client.get('/groups/delete/'+str(self.group_design_id2)+'/')
        self.assertEqual(response.status_code//100, 2)
        self.client.logout()
        try:
            design = Design.objects.get(id=self.group_design_id2)
            self.assertEqual(1, 2)
        except Design.DoesNotExist:
            pass


    # Delete UnExisting Design
    def test_unexisting(self):
        did=100
        try:
            design = Design.objects.get(id=did)
            self.assertEqual(1, 2)
        except Design.DoesNotExist:
            pass
        self.client.login(username='delete1',password='pass')
        response = self.client.get('/groups/delete/'+str(did)+'/')
        self.assertEqual(response.status_code//100, 4)
        self.client.logout()

## Like/UnLike Design
class LikeDesignCase(TestCase):
    def setUp(self):
        self.client.post('/users/', {'username': 'like1', 'password': 'pass'})
        self.client.post('/users/', {'username': 'like2', 'password': 'pass'})
        self.client.login(username='like1',password='pass')
        self.client.post('/create_group/', "{\"grouptype\": \"MJ\", \"groupname\": \"like_group\"}", content_type='application/json')
        self.group = Group.objects.get(group_name='like_group')
        response = self.client.get('/')
        response.render()
        stream = io.BytesIO(response.content)
        data = JSONParser().parse(stream)
        design_id = data['id']
        design_data = """{
            \"id\": """ + str(design_id) + """,
            \"design\": {
                \"body\": \"#fcfcfc\",
                \"button\": \"#fcfcfc\",
                \"sleeve\": \"#fcfcfc\",
                \"banding\": \"#fcfcfc\",
                \"stripe\": \"#fcfcfc\"
            },
            \"text\": {
                \"frontchest\": {
                    \"id\": null,
                    \"textvalue\": \"S\",
                    \"fontFamily\": \"arial\",
                    \"fill\": \"#3f51b5\",
                    \"fontStyle\": \"bold\",
                    \"fontSize\": 50,
                    \"left\": 250,
                    \"top\": 110,
                    \"stroke\": \"#000000\",
                    \"strokeWidth\": 2
                },
                \"rightarm\": {
                    \"id\": null,
                    \"textvalue\": \"19\",
                    \"fontFamily\": \"arial\",
                    \"fill\": \"#607d8b\",
                    \"fontStyle\": \"bold\",
                    \"fontSize\": 50,
                    \"left\": 50,
                    \"top\": 120,
                    \"stroke\": \"\",
                    \"strokeWidth\": 0
                },
                \"upperback\": {
                    \"id\": null,
                    \"textvalue\": \"SEOUL NAT'L\",
                    \"fontFamily\": \"arial\",
                    \"fill\": \"#ffc107\",
                    \"fontStyle\": \"bold\",
                    \"fontSize\": 25,
                    \"left\": 135,
                    \"top\": 125,
                    \"stroke\": \"\",
                    \"strokeWidth\": 0
                },
                \"middleback\": {
                    \"id\": null,
                    \"textvalue\": \"UNIVERSITY\",
                    \"fontFamily\": \"arial\",
                    \"fill\": \"#ffc107\",
                    \"fontStyle\": \"bold\",
                    \"fontSize\": 20,
                    \"left\": 155,
                    \"top\": 155,
                    \"stroke\": \"\",
                    \"strokeWidth\": 0
                },
                \"lowerback\": {
                    \"id\": null,
                    \"textvalue\": \"hi\",
                    \"fontFamily\": \"arial\",
                    \"fill\": \"#ffc107\",
                    \"fontStyle\": \"bold\",
                    \"fontSize\": 15,
                    \"left\": 150,
                    \"top\": 190,
                    \"stroke\": \"\",
                    \"strokeWidth\": 0
                }
            },
            \"logo\": {
                \"front\": {
                    \"id\": null,
                    \"src\": \"hi\",
                    \"width\": 571,
                    \"height\": 589,
                    \"left\": 340,
                    \"top\": 180,
                    \"scaleX\": 1,
                    \"scaleY\": 1
                },
                \"back\": {
                    \"id\": null,
                    \"src\": \"hi\",
                    \"width\": 571,
                    \"height\": 589,
                    \"left\": 215,
                    \"top\": 280,
                    \"scaleX\": 1,
                    \"scaleY\": 1
                }
            },
            \"image\": {
                \"frontImg\": null,
                \"backImg\": null
            }
        }"""
        self.client.put(path='/', data=design_data, content_type='application/json')
        response = self.client.get('/groups/'+str(self.group.id)+'/post/'+str(design_id)+'/')
        response.render()
        stream = io.BytesIO(response.content)
        data = JSONParser().parse(stream)
        self.group_design_id = data['id']
        self.client.logout()

    # Like Design without Login
    # Non-Member Like Design
    def test_without_auth(self):
        self.client.logout()
        response = self.client.get('/groups/like/'+str(self.group_design_id)+'/')
        self.assertEqual(response.status_code//100, 4)
        self.client.login(username='like2',password='pass')
        response = self.client.get('/groups/like/'+str(self.group_design_id)+'/')
        self.assertEqual(response.status_code//100, 4)
        self.client.logout()

    # Like Design
    # UnLike Design
    def test_like_design(self):
        design = Design.objects.get(id=self.group_design_id)
        user = User.objects.get(username="like1")
        self.assertEqual(design.likes, 0)
        self.assertTrue(user not in design.who.all())
        self.client.login(username='like1',password='pass')
        response = self.client.get('/groups/like/'+str(self.group_design_id)+'/')
        self.assertEqual(response.status_code//100, 2)
        design = Design.objects.get(id=self.group_design_id)
        self.assertEqual(design.likes, 1)
        self.assertTrue(user in design.who.all())
        response = self.client.get('/groups/unlike/'+str(self.group_design_id)+'/')
        self.assertEqual(response.status_code//100, 2)
        design = Design.objects.get(id=self.group_design_id)
        self.assertEqual(design.likes, 0)
        self.assertTrue(user not in design.who.all())
        self.client.logout()

    # Double Like Design
    def test_with_dups(self):
        self.client.login(username='like1',password='pass')
        response = self.client.get('/groups/like/'+str(self.group_design_id)+'/')
        response = self.client.get('/groups/like/'+str(self.group_design_id)+'/')
        self.assertEqual(response.status_code//100, 4)
        self.client.logout()

## Add Comment
class AddCommentCase(TestCase):
    def setUp(self):
        self.client.post('/users/', {'username': 'comment1', 'password': 'pass'})
        self.client.post('/users/', {'username': 'comment2', 'password': 'pass'})
        self.client.login(username='comment1',password='pass')
        self.client.post('/create_group/', "{\"grouptype\": \"MJ\", \"groupname\": \"comment_group\"}", content_type='application/json')
        self.group = Group.objects.get(group_name='comment_group')
        response = self.client.get('/')
        response.render()
        stream = io.BytesIO(response.content)
        data = JSONParser().parse(stream)
        design_id = data['id']
        design_data = """{
            \"id\": """ + str(design_id) + """,
            \"design\": {
                \"body\": \"#fcfcfc\",
                \"button\": \"#fcfcfc\",
                \"sleeve\": \"#fcfcfc\",
                \"banding\": \"#fcfcfc\",
                \"stripe\": \"#fcfcfc\"
            },
            \"text\": {
                \"frontchest\": {
                    \"id\": null,
                    \"textvalue\": \"S\",
                    \"fontFamily\": \"arial\",
                    \"fill\": \"#3f51b5\",
                    \"fontStyle\": \"bold\",
                    \"fontSize\": 50,
                    \"left\": 250,
                    \"top\": 110,
                    \"stroke\": \"#000000\",
                    \"strokeWidth\": 2
                },
                \"rightarm\": {
                    \"id\": null,
                    \"textvalue\": \"19\",
                    \"fontFamily\": \"arial\",
                    \"fill\": \"#607d8b\",
                    \"fontStyle\": \"bold\",
                    \"fontSize\": 50,
                    \"left\": 50,
                    \"top\": 120,
                    \"stroke\": \"\",
                    \"strokeWidth\": 0
                },
                \"upperback\": {
                    \"id\": null,
                    \"textvalue\": \"SEOUL NAT'L\",
                    \"fontFamily\": \"arial\",
                    \"fill\": \"#ffc107\",
                    \"fontStyle\": \"bold\",
                    \"fontSize\": 25,
                    \"left\": 135,
                    \"top\": 125,
                    \"stroke\": \"\",
                    \"strokeWidth\": 0
                },
                \"middleback\": {
                    \"id\": null,
                    \"textvalue\": \"UNIVERSITY\",
                    \"fontFamily\": \"arial\",
                    \"fill\": \"#ffc107\",
                    \"fontStyle\": \"bold\",
                    \"fontSize\": 20,
                    \"left\": 155,
                    \"top\": 155,
                    \"stroke\": \"\",
                    \"strokeWidth\": 0
                },
                \"lowerback\": {
                    \"id\": null,
                    \"textvalue\": \"hi\",
                    \"fontFamily\": \"arial\",
                    \"fill\": \"#ffc107\",
                    \"fontStyle\": \"bold\",
                    \"fontSize\": 15,
                    \"left\": 150,
                    \"top\": 190,
                    \"stroke\": \"\",
                    \"strokeWidth\": 0
                }
            },
            \"logo\": {
                \"front\": {
                    \"id\": null,
                    \"src\": \"hi\",
                    \"width\": 571,
                    \"height\": 589,
                    \"left\": 340,
                    \"top\": 180,
                    \"scaleX\": 1,
                    \"scaleY\": 1
                },
                \"back\": {
                    \"id\": null,
                    \"src\": \"hi\",
                    \"width\": 571,
                    \"height\": 589,
                    \"left\": 215,
                    \"top\": 280,
                    \"scaleX\": 1,
                    \"scaleY\": 1
                }
            },
            \"image\": {
                \"frontImg\": null,
                \"backImg\": null
            }
        }"""
        self.client.put(path='/', data=design_data, content_type='application/json')
        response = self.client.get('/groups/'+str(self.group.id)+'/post/'+str(design_id)+'/')
        response.render()
        stream = io.BytesIO(response.content)
        data = JSONParser().parse(stream)
        self.group_design_id = data['id']
        self.client.logout()

    # Add Comment without Login
    def test_without_auth(self):
        self.client.logout()
        response = self.client.post('/groups/comment/'+str(self.group_design_id)+'/', "{\"name\":\"name\",\"comment\":\"hi\"}", content_type='application/json')
        self.assertEqual(response.status_code//100, 4)
    
    # Add Comment
    # Non-Member Add Comment
    def test_add_comment(self):
        self.client.login(username='comment1',password='pass')
        response = self.client.post('/groups/comment/'+str(self.group_design_id)+'/', "{\"name\":\"name\",\"comment\":\"hi\"}", content_type='application/json')
        self.assertEqual(response.status_code//100, 2)
        self.client.logout()
        self.client.login(username='comment2',password='pass')
        response = self.client.post('/groups/comment/'+str(self.group_design_id)+'/', "{\"name\":\"name\",\"comment\":\"hi\"}", content_type='application/json')
        self.assertEqual(response.status_code//100, 2)
        self.client.logout()

## Like/Unlike Comment
class LikeCommentCase(TestCase):
    def setUp(self):
        self.client.post('/users/', {'username': 'likecomment1', 'password': 'pass'})
        self.client.post('/users/', {'username': 'likecomment2', 'password': 'pass'})
        self.client.login(username='likecomment1',password='pass')
        self.client.post('/create_group/', "{\"grouptype\": \"MJ\", \"groupname\": \"likecomment_group\"}", content_type='application/json')
        self.group = Group.objects.get(group_name='likecomment_group')
        response = self.client.get('/')
        response.render()
        stream = io.BytesIO(response.content)
        data = JSONParser().parse(stream)
        design_id = data['id']
        design_data = """{
            \"id\": """ + str(design_id) + """,
            \"design\": {
                \"body\": \"#fcfcfc\",
                \"button\": \"#fcfcfc\",
                \"sleeve\": \"#fcfcfc\",
                \"banding\": \"#fcfcfc\",
                \"stripe\": \"#fcfcfc\"
            },
            \"text\": {
                \"frontchest\": {
                    \"id\": null,
                    \"textvalue\": \"S\",
                    \"fontFamily\": \"arial\",
                    \"fill\": \"#3f51b5\",
                    \"fontStyle\": \"bold\",
                    \"fontSize\": 50,
                    \"left\": 250,
                    \"top\": 110,
                    \"stroke\": \"#000000\",
                    \"strokeWidth\": 2
                },
                \"rightarm\": {
                    \"id\": null,
                    \"textvalue\": \"19\",
                    \"fontFamily\": \"arial\",
                    \"fill\": \"#607d8b\",
                    \"fontStyle\": \"bold\",
                    \"fontSize\": 50,
                    \"left\": 50,
                    \"top\": 120,
                    \"stroke\": \"\",
                    \"strokeWidth\": 0
                },
                \"upperback\": {
                    \"id\": null,
                    \"textvalue\": \"SEOUL NAT'L\",
                    \"fontFamily\": \"arial\",
                    \"fill\": \"#ffc107\",
                    \"fontStyle\": \"bold\",
                    \"fontSize\": 25,
                    \"left\": 135,
                    \"top\": 125,
                    \"stroke\": \"\",
                    \"strokeWidth\": 0
                },
                \"middleback\": {
                    \"id\": null,
                    \"textvalue\": \"UNIVERSITY\",
                    \"fontFamily\": \"arial\",
                    \"fill\": \"#ffc107\",
                    \"fontStyle\": \"bold\",
                    \"fontSize\": 20,
                    \"left\": 155,
                    \"top\": 155,
                    \"stroke\": \"\",
                    \"strokeWidth\": 0
                },
                \"lowerback\": {
                    \"id\": null,
                    \"textvalue\": \"hi\",
                    \"fontFamily\": \"arial\",
                    \"fill\": \"#ffc107\",
                    \"fontStyle\": \"bold\",
                    \"fontSize\": 15,
                    \"left\": 150,
                    \"top\": 190,
                    \"stroke\": \"\",
                    \"strokeWidth\": 0
                }
            },
            \"logo\": {
                \"front\": {
                    \"id\": null,
                    \"src\": \"hi\",
                    \"width\": 571,
                    \"height\": 589,
                    \"left\": 340,
                    \"top\": 180,
                    \"scaleX\": 1,
                    \"scaleY\": 1
                },
                \"back\": {
                    \"id\": null,
                    \"src\": \"hi\",
                    \"width\": 571,
                    \"height\": 589,
                    \"left\": 215,
                    \"top\": 280,
                    \"scaleX\": 1,
                    \"scaleY\": 1
                }
            },
            \"image\": {
                \"frontImg\": null,
                \"backImg\": null
            }
        }"""
        self.client.put(path='/', data=design_data, content_type='application/json')
        response = self.client.get('/groups/'+str(self.group.id)+'/post/'+str(design_id)+'/')
        response.render()
        stream = io.BytesIO(response.content)
        data = JSONParser().parse(stream)
        self.group_design_id = data['id']
        response = self.client.post('/groups/comment/'+str(self.group_design_id)+'/', "{\"name\":\"name\",\"comment\":\"hi\"}", content_type='application/json')
        response.render()
        stream = io.BytesIO(response.content)
        data = JSONParser().parse(stream)
        self.comment_id = data[0]['id']
        self.client.logout()

    # Like Comment without Login
    def test_without_auth(self):
        self.client.logout()
        response = self.client.get('/groups/comment/like/'+str(self.comment_id)+'/')
        self.assertEqual(response.status_code//100, 4)

    # Like Comment
    # UnLike Comment
    # Non-Member Like Comment
    def test_like_comment(self):
        comment = Comment.objects.get(id=self.comment_id)
        user1 = User.objects.get(username="likecomment1")
        user2 = User.objects.get(username="likecomment2")
        self.assertEqual(comment.likes, 0)
        self.assertTrue(user1 not in comment.who_c.all())
        self.client.login(username='likecomment1',password='pass')
        response = self.client.get('/groups/comment/like/'+str(self.comment_id)+'/')
        self.assertEqual(response.status_code//100, 2)
        comment = Comment.objects.get(id=self.comment_id)
        self.assertEqual(comment.likes, 1)
        self.assertTrue(user1 in comment.who_c.all())
        response = self.client.get('/groups/comment/unlike/'+str(self.comment_id)+'/')
        self.assertEqual(response.status_code//100, 2)
        comment = Comment.objects.get(id=self.comment_id)
        self.assertEqual(comment.likes, 0)
        self.assertTrue(user1 not in comment.who_c.all())
        self.client.logout()
        self.client.login(username='likecomment2',password='pass')
        self.assertTrue(user2 not in comment.who_c.all())
        response = self.client.get('/groups/comment/like/'+str(self.comment_id)+'/')
        self.assertEqual(response.status_code//100, 2)
        comment = Comment.objects.get(id=self.comment_id)
        self.assertEqual(comment.likes, 1)
        self.assertTrue(user2 in comment.who_c.all())

    # Double Like Comment
    def test_with_dups(self):
        self.client.login(username='likecomment1',password='pass')
        response = self.client.get('/groups/comment/like/'+str(self.comment_id)+'/')
        response = self.client.get('/groups/comment/like/'+str(self.comment_id)+'/')
        self.assertEqual(response.status_code//100, 4)

## Update/Delete Comment
class UpdateCommentCase(TestCase):
    def setUp(self):
        self.client.post('/users/', {'username': 'updatecomment1', 'password': 'pass'})
        self.client.post('/users/', {'username': 'updatecomment2', 'password': 'pass'})
        self.client.login(username='updatecomment1',password='pass')
        self.client.post('/create_group/', "{\"grouptype\": \"MJ\", \"groupname\": \"updatecomment_group\"}", content_type='application/json')
        self.group = Group.objects.get(group_name='updatecomment_group')
        response = self.client.get('/')
        response.render()
        stream = io.BytesIO(response.content)
        data = JSONParser().parse(stream)
        design_id = data['id']
        design_data = """{
            \"id\": """ + str(design_id) + """,
            \"design\": {
                \"body\": \"#fcfcfc\",
                \"button\": \"#fcfcfc\",
                \"sleeve\": \"#fcfcfc\",
                \"banding\": \"#fcfcfc\",
                \"stripe\": \"#fcfcfc\"
            },
            \"text\": {
                \"frontchest\": {
                    \"id\": null,
                    \"textvalue\": \"S\",
                    \"fontFamily\": \"arial\",
                    \"fill\": \"#3f51b5\",
                    \"fontStyle\": \"bold\",
                    \"fontSize\": 50,
                    \"left\": 250,
                    \"top\": 110,
                    \"stroke\": \"#000000\",
                    \"strokeWidth\": 2
                },
                \"rightarm\": {
                    \"id\": null,
                    \"textvalue\": \"19\",
                    \"fontFamily\": \"arial\",
                    \"fill\": \"#607d8b\",
                    \"fontStyle\": \"bold\",
                    \"fontSize\": 50,
                    \"left\": 50,
                    \"top\": 120,
                    \"stroke\": \"\",
                    \"strokeWidth\": 0
                },
                \"upperback\": {
                    \"id\": null,
                    \"textvalue\": \"SEOUL NAT'L\",
                    \"fontFamily\": \"arial\",
                    \"fill\": \"#ffc107\",
                    \"fontStyle\": \"bold\",
                    \"fontSize\": 25,
                    \"left\": 135,
                    \"top\": 125,
                    \"stroke\": \"\",
                    \"strokeWidth\": 0
                },
                \"middleback\": {
                    \"id\": null,
                    \"textvalue\": \"UNIVERSITY\",
                    \"fontFamily\": \"arial\",
                    \"fill\": \"#ffc107\",
                    \"fontStyle\": \"bold\",
                    \"fontSize\": 20,
                    \"left\": 155,
                    \"top\": 155,
                    \"stroke\": \"\",
                    \"strokeWidth\": 0
                },
                \"lowerback\": {
                    \"id\": null,
                    \"textvalue\": \"hi\",
                    \"fontFamily\": \"arial\",
                    \"fill\": \"#ffc107\",
                    \"fontStyle\": \"bold\",
                    \"fontSize\": 15,
                    \"left\": 150,
                    \"top\": 190,
                    \"stroke\": \"\",
                    \"strokeWidth\": 0
                }
            },
            \"logo\": {
                \"front\": {
                    \"id\": null,
                    \"src\": \"hi\",
                    \"width\": 571,
                    \"height\": 589,
                    \"left\": 340,
                    \"top\": 180,
                    \"scaleX\": 1,
                    \"scaleY\": 1
                },
                \"back\": {
                    \"id\": null,
                    \"src\": \"hi\",
                    \"width\": 571,
                    \"height\": 589,
                    \"left\": 215,
                    \"top\": 280,
                    \"scaleX\": 1,
                    \"scaleY\": 1
                }
            },
            \"image\": {
                \"frontImg\": null,
                \"backImg\": null
            }
        }"""
        self.client.put(path='/', data=design_data, content_type='application/json')
        response = self.client.get('/groups/'+str(self.group.id)+'/post/'+str(design_id)+'/')
        response.render()
        stream = io.BytesIO(response.content)
        data = JSONParser().parse(stream)
        self.group_design_id = data['id']
        response = self.client.post('/groups/comment/'+str(self.group_design_id)+'/', "{\"name\":\"name\",\"comment\":\"hi\"}", content_type='application/json')
        response.render()
        stream = io.BytesIO(response.content)
        data = JSONParser().parse(stream)
        self.comment_id1 = data[0]['id']
        response = self.client.post('/groups/comment/'+str(self.group_design_id)+'/', "{\"name\":\"name\",\"comment\":\"hi\"}", content_type='application/json')
        response.render()
        stream = io.BytesIO(response.content)
        data = JSONParser().parse(stream)
        self.comment_id2 = data[0]['id']
        self.client.logout()
        self.client.login(username='updatecomment2', password='pass')
        self.client.get('/join_group/' + str(self.group.id) + '/')
        self.client.logout()

    # Edit Comment
    # Delete Comment
    def test_update_comment(self):
        comment_before = Comment.objects.get(id=self.comment_id1)
        self.client.login(username='updatecomment1', password='pass')
        response = self.client.put('/groups/comment/'+str(self.group_design_id)+'/'+str(self.comment_id1)+'/', "{\"name\":\"namely\",\"comment\":\"hello\"}", content_type='application/json')
        self.assertEqual(response.status_code//100, 2)
        comment_after = Comment.objects.get(id=self.comment_id1)
        self.assertEqual(comment_before.id, comment_after.id)
        self.assertFalse(comment_before.name == comment_after.name)
        self.assertFalse(comment_before.comment == comment_after.comment)
        response = self.client.delete('/groups/comment/'+str(self.group_design_id)+'/'+str(self.comment_id1)+'/')
        self.assertEqual(response.status_code//100, 2)
        try:
            comment = Comment.objects.get(id=self.comment_id1)
            self.assertEqual(1, 2)
        except Comment.DoesNotExist:
            pass
        self.client.logout()
        

    # Update Comment without Login
    # Non-Owner Update Comment
    def test_without_auth(self):
        self.client.logout()
        response = self.client.put('/groups/comment/'+str(self.group_design_id)+'/'+str(self.comment_id2)+'/', "{\"name\":\"namely\",\"comment\":\"hello\"}", content_type='application/json')
        self.assertEqual(response.status_code//100, 4)
        self.client.login(username='updatecomment2', password='pass')
        response = self.client.put('/groups/comment/'+str(self.group_design_id)+'/'+str(self.comment_id2)+'/', "{\"name\":\"namely\",\"comment\":\"hello\"}", content_type='application/json')
        self.assertEqual(response.status_code//100, 4)
        self.client.logout()

    # Admin Update Comment
    def test_admin(self):
        user = User.objects.get(username="updatecomment2")
        comment_before = Comment.objects.get(id=self.comment_id2)
        self.client.login(username='updatecomment1', password='pass')
        self.client.put('/groups/' + str(self.group.id) + '/members/' + str(user.id) + '/')
        self.client.logout()
        self.client.login(username='updatecomment2', password='pass')
        response = self.client.put('/groups/comment/'+str(self.group_design_id)+'/'+str(self.comment_id2)+'/', "{\"name\":\"namely\",\"comment\":\"hello\"}", content_type='application/json')
        self.assertEqual(response.status_code//100, 2)
        comment_after = Comment.objects.get(id=self.comment_id2)
        self.assertEqual(comment_before.id, comment_after.id)
        self.assertFalse(comment_before.name == comment_after.name)
        self.assertFalse(comment_before.comment == comment_after.comment)
        response = self.client.delete('/groups/comment/'+str(self.group_design_id)+'/'+str(self.comment_id2)+'/')
        self.assertEqual(response.status_code//100, 2)
        try:
            comment = Comment.objects.get(id=self.comment_id2)
            self.assertEqual(1, 2)
        except Comment.DoesNotExist:
            pass
        self.client.logout()
