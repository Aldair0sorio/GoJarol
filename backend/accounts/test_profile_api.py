"""Account API regressions on an isolated in-memory test database."""
import pytest
pytest.importorskip('django')
from django.conf import settings
if not settings.configured:
    settings.configure(SECRET_KEY='test-profile-only', ROOT_URLCONF=__name__, ALLOWED_HOSTS=['testserver'],
        DATABASES={'default': {'ENGINE':'django.db.backends.sqlite3','NAME':':memory:'}},
        INSTALLED_APPS=['django.contrib.auth','django.contrib.contenttypes','django.contrib.sessions','rest_framework.authtoken','accounts','progress'],
        AUTH_USER_MODEL='accounts.User', MIDDLEWARE=['django.contrib.sessions.middleware.SessionMiddleware'],
        REST_FRAMEWORK={'DEFAULT_AUTHENTICATION_CLASSES':['accounts.authentication.VerifiedTokenAuthentication'],
                        'DEFAULT_PERMISSION_CLASSES':['rest_framework.permissions.IsAuthenticated']})
import django
django.setup()
from django.urls import path
from accounts.views import MeView, LoginView, LogoutView, GoogleLoginView
from accounts.models import User
from django.core.management import call_command
from rest_framework.test import APIClient
from chat.views import ChatMessageView
from progress.views import MyProgressView
urlpatterns=[path('auth/google/',GoogleLoginView.as_view()),path('chat/messages/',ChatMessageView.as_view()),path('auth/me/',MeView.as_view()),path('auth/login/',LoginView.as_view()),path('auth/logout/',LogoutView.as_view())]
urlpatterns.append(path('progress/me/', MyProgressView.as_view()))

@pytest.fixture(scope='module',autouse=True)
def database():
    call_command('migrate',verbosity=0,interactive=False)

@pytest.fixture
def client():
    username=f'profile_{User.objects.count()}'
    user=User.objects.create_user(username=username,password='Profile-test-only-429!',email=f'{username}@example.test',nivel='secundaria',grado=1)
    client=APIClient()
    result=client.post('/auth/login/',{'username':username,'password':'Profile-test-only-429!'},format='json')
    assert result.status_code==200
    client.credentials(HTTP_AUTHORIZATION='Token '+result.data['token'])
    return client,user

def test_profile_load_save_and_logout(client):
    c,user=client
    result=c.get('/auth/me/')
    assert result.status_code==200 and result.data['id']==user.id
    assert {'first_name','last_name','username','email','rol','nivel','grado'} <= result.data.keys()
    result=c.patch('/auth/me/',{'first_name':'María','last_name':'López','nivel':'bachillerato','grado':6},format='json')
    assert result.status_code==200
    user.refresh_from_db()
    assert user.first_name=='María' and user.grado==6
    assert c.post('/auth/logout/').status_code==204
    assert c.get('/auth/me/').status_code==401

@pytest.mark.parametrize('field,value',[('rol','admin'),('is_staff',True),('is_superuser',True),('id',999),('username','other'),('email','other@example.test'),('password','changed'),('email_status','verified'),('email_verified_at','2026-01-01T00:00:00Z')])
def test_protected_fields_and_other_accounts_cannot_be_changed(client,field,value):
    c,user=client
    assert c.patch('/auth/me/',{field:value},format='json').status_code==400
    user.refresh_from_db()
    assert user.rol=='estudiante' and not user.is_staff and not user.is_superuser

@pytest.mark.parametrize('data',[{'grado':4},{'grado':0},{'nivel':'universidad'},{'nivel':'bachillerato','grado':7}])
def test_academic_limits(client,data):
    c,_=client
    assert c.patch('/auth/me/',data,format='json').status_code==400

@pytest.mark.parametrize('role',['docente','admin'])
def test_teacher_and_admin_personal_details_remain_editable(client,role):
    c,user=client
    user.rol=role;user.save()
    assert c.get('/auth/me/').data['rol']==role
    assert c.patch('/auth/me/',{'first_name':'Ana'},format='json').status_code==200
    assert c.patch('/auth/me/',{'grado':2},format='json').status_code==400

def test_guest_cannot_read_or_edit_profile():
    c=APIClient()
    assert c.get('/auth/me/').status_code==401
    assert c.patch('/auth/me/',{'first_name':'Otro'},format='json').status_code==401
    assert c.post('/auth/logout/').status_code==401


def test_login_by_email_and_chat_remain_available(client):
    c,user=client
    visitor=APIClient()
    login=visitor.post('/auth/login/',{'username':user.email,'password':'Profile-test-only-429!'},format='json')
    assert login.status_code==200
    visitor.credentials(HTTP_AUTHORIZATION='Token '+login.data['token'])
    chat=visitor.post('/chat/messages/',{'message':'Explícame las fracciones'},format='json')
    assert chat.status_code==200 and chat.data['type']=='explanation'
    assert c.patch('/auth/me/',{'first_name':'Nombre guardado'},format='json').status_code==200
    assert visitor.get('/auth/me/').data['first_name']=='Nombre guardado'
    assert visitor.get('/auth/me/').data['rol']=='estudiante'


def test_guest_chat_is_private_and_bad_login_does_not_create_a_session():
    visitor=APIClient()
    assert visitor.get('/auth/me/').status_code==401
    bad=visitor.post('/auth/login/',{'username':'missing','password':'incorrect'},format='json')
    assert bad.status_code==401 and 'token' not in bad.data
    chat=visitor.post('/chat/messages/',{'message':'Explícame las fracciones'},format='json')
    assert chat.status_code==401


# Offline crypto tests exercise google-auth itself; only Google's certificate HTTP response is replaced.
import json
import time
from types import SimpleNamespace
from unittest.mock import patch
from django.test import override_settings
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from google.auth import crypt, jwt
from accounts.models import GoogleIdentity
from rest_framework.authtoken.models import Token

@pytest.fixture(scope='module')
def google_keys():
    key=rsa.generate_private_key(public_exponent=65537,key_size=2048)
    private=key.private_bytes(serialization.Encoding.PEM,serialization.PrivateFormat.PKCS8,serialization.NoEncryption())
    public=key.public_key().public_bytes(serialization.Encoding.PEM,serialization.PublicFormat.SubjectPublicKeyInfo).decode()
    return private, public


def google_claims(subject='offline-subject',email='offline@example.test'):
    return dict(sub=subject,email=email,email_verified=True,aud='test-client',iss='https://accounts.google.com',
                exp=int(time.time())+3600,iat=int(time.time())-10,name='Nombre verificado')


def google_post(claims,keys,extra=None,wrong_key=False):
    private,public=keys
    if wrong_key:
        private=rsa.generate_private_key(public_exponent=65537,key_size=2048).private_bytes(
            serialization.Encoding.PEM,serialization.PrivateFormat.PKCS8,serialization.NoEncryption())
    encoded=jwt.encode(crypt.RSASigner.from_string(private),claims,key_id='offline-key').decode()
    certs=SimpleNamespace(status=200,data=json.dumps({'offline-key':public}).encode())
    with override_settings(GOOGLE_CLIENT_ID='test-client'), patch('accounts.google_identity.VerificationRequest',return_value=lambda *a,**k:certs):
        return APIClient().post('/auth/google/',{'credential':encoded,**(extra or {})},format='json')


def test_google_verified_subject_creates_once_and_ignores_client_identity(google_keys):
    claims=google_claims()
    result=google_post(claims,google_keys,{'email':'attacker@example.test','name':'Nombre falso'})
    assert result.status_code==200
    assert result.data['user']['email']==claims['email']
    assert result.data['user']['email_status']=='verified'
    assert result.data['user']['alias']=='Nombre verificado'
    count=User.objects.count()
    again=google_post(claims,google_keys)
    assert again.status_code==200 and again.data['user']['id']==result.data['user']['id']
    assert User.objects.count()==count
    assert GoogleIdentity.objects.get(subject=claims['sub']).user_id==result.data['user']['id']


@pytest.mark.parametrize('field,value',[('aud','wrong-client'),('iss','https://attacker.test'),('exp',1),('iat',9999999999),('email_verified',False),('email_verified','true'),('sub',''),('email','invalid')])
def test_google_invalid_claims_do_not_create_users_or_tokens(google_keys,field,value):
    before=(User.objects.count(),Token.objects.count(),GoogleIdentity.objects.count())
    claims=google_claims('invalid-'+field);claims[field]=value
    result=google_post(claims,google_keys)
    assert result.status_code==401
    assert 'token' not in result.data
    assert before==(User.objects.count(),Token.objects.count(),GoogleIdentity.objects.count())


def test_google_wrong_signature_is_rejected(google_keys):
    before=User.objects.count()
    assert google_post(google_claims('forged'),google_keys,wrong_key=True).status_code==401
    assert User.objects.count()==before


@pytest.mark.parametrize('data',[{}, {'email':'someone@example.test'}, {'credential':''}, {'credential':123}, {'credential':'x'*8193}])
def test_google_requires_real_credential(data):
    with override_settings(GOOGLE_CLIENT_ID='test-client'):
        response=APIClient().post('/auth/google/',data,format='json')
    assert response.status_code==400 and 'token' not in response.data


def test_google_never_links_existing_email_automatically(client,google_keys):
    _,user=client
    before=User.objects.count()
    response=google_post(google_claims('unlinked-sub',user.email),google_keys)
    assert response.status_code==409 and 'token' not in response.data
    assert User.objects.count()==before and not GoogleIdentity.objects.filter(subject='unlinked-sub').exists()


def test_google_inactive_linked_account_cannot_login(google_keys):
    user=User.objects.create_user(username='google_disabled',email='disabled@example.test',is_active=False)
    GoogleIdentity.objects.create(subject='disabled-sub',email=user.email,user=user)
    response=google_post(google_claims('disabled-sub',user.email),google_keys)
    assert response.status_code==403 and not Token.objects.filter(user=user).exists()


def test_google_missing_configuration_and_transport_fail_closed():
    from google.auth.exceptions import TransportError
    before=User.objects.count()
    with override_settings(GOOGLE_CLIENT_ID=''):
        assert APIClient().post('/auth/google/',{'credential':'token'},format='json').status_code==503
    with override_settings(GOOGLE_CLIENT_ID='test-client'), patch('accounts.google_identity.id_token.verify_oauth2_token',side_effect=TransportError('offline')):
        result=APIClient().post('/auth/google/',{'credential':'token'},format='json')
    assert result.status_code==503 and 'token' not in result.data
    assert User.objects.count()==before


def test_google_email_change_requires_review(google_keys):
    claims=google_claims('changed-sub','first@example.test')
    assert google_post(claims,google_keys).status_code==200
    claims['email']='second@example.test'
    assert google_post(claims,google_keys).status_code==409
    assert GoogleIdentity.objects.get(subject='changed-sub').email=='first@example.test'


@pytest.mark.parametrize('credential', ['not-a-jwt', 'a.b.c', 'eyJhbGciOiJub25lIn0.e30.'])
def test_google_malformed_or_unsigned_tokens_fail_closed(google_keys, credential):
    certs=SimpleNamespace(status=200,data=json.dumps({'offline-key':google_keys[1]}).encode())
    before=(User.objects.count(),Token.objects.count())
    with override_settings(GOOGLE_CLIENT_ID='test-client'), patch('accounts.google_identity.VerificationRequest',return_value=lambda *a,**k:certs):
        result=APIClient().post('/auth/google/',{'credential':credential},format='json')
    assert result.status_code==401 and 'token' not in result.data
    assert before==(User.objects.count(),Token.objects.count())


def test_google_cannot_self_register_as_admin(google_keys):
    response=google_post(google_claims('admin-attempt','admin-attempt@example.test'),google_keys,{'role':'admin'})
    assert response.status_code==400 and not GoogleIdentity.objects.filter(subject='admin-attempt').exists()


def test_google_existing_role_is_not_overwritten(google_keys):
    claims=google_claims('teacher-sub','teacher-sub@example.test')
    result=google_post(claims,google_keys,{'role':'docente'})
    assert result.status_code==200 and result.data['user']['rol']=='docente'
    again=google_post(claims,google_keys,{'role':'admin'})
    assert again.status_code==200 and again.data['user']['rol']=='docente'


def test_google_different_subject_cannot_claim_same_email(google_keys):
    claims=google_claims('first-owner','same-email@example.test')
    assert google_post(claims,google_keys).status_code==200
    claims['sub']='second-owner'
    assert google_post(claims,google_keys).status_code==409
    assert not GoogleIdentity.objects.filter(subject='second-owner').exists()


def test_guest_identity_headers_cannot_access_private_progress(client):
    _,user=client
    from progress.models import StudentProgress
    progress,_=StudentProgress.objects.get_or_create(user=user)
    progress.xp=4321; progress.save()
    response=APIClient().get('/progress/me/',{'user_id':user.id,'user_email':user.email},
        HTTP_X_JAROL_USER_ID=str(user.id),HTTP_X_JAROL_USER_EMAIL=user.email,HTTP_X_JAROL_USER_NAME=user.username)
    assert response.status_code==200 and response.data['xp']==0


def test_authenticated_progress_uses_token_not_identity_headers(client):
    c,user=client
    from progress.models import StudentProgress
    progress,_=StudentProgress.objects.get_or_create(user=user)
    progress.xp=99;progress.save()
    response=c.get('/progress/me/',HTTP_X_JAROL_USER_ID='999999',HTTP_X_JAROL_USER_EMAIL='other@example.test')
    assert response.status_code==200 and response.data['xp']==99
