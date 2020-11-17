# -*- coding: utf_8 -*-
import requests
import random
import string
import time
from flask import *
from flask_google_recaptcha import *
from django.conf import settings
from django.shortcuts import render
from django.http import JsonResponse
from json import JSONEncoder
from django.views.decorators.csrf import csrf_exempt
from web.models import  *
from datetime import datetime
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from postmark import PMMail

# Create your views here.


random_str = lambda N:''.join(random.SystemRandom().choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(N))

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def grecaptcha_verify(request):
    data = request.POST
    captcha_rs = data.get('g-recaptcha-response')
    url = "http://www.google.com/recaptcha/api/siteverify"
    params = {'secret':settings.RECAPTCHA_PRIVATE_KEY,'response':captcha_rs,'remoteip':get_client_ip(request)}
    verify_rs = request.GET.get(url,params )
  
    return verify_rs





def register(request):
    if 'requestcode' in request.POST:
        if not grecaptcha_verify(request):
            context = {'message':'کپچای گوگل درست وارد نشده بود. شاید ربات هستید؟ کد یا کلیک یا تشخیص عکس زیر فرم را درست پر کنید. ببخشید که فرم به شکل اولیه برنگشته!'}
            return render(request,'register.html',context)
        if User.objects.filter(email=request.POST['email']).exists():
            context = {  'message': 'متاسفانه این ایمیل قبلا استفاده شده است. در صورتی که این ایمیل شما است، از صفحه ورود گزینه فراموشی پسورد رو انتخاب کنین. ببخشید که فرم ذخیره نشده. درست می شه'}  # TODO: forgot password

            # TODO: keep the form data
            return render(request, 'register.html', context)
       
        if not User.objects.filter(email=request.POST['email']).exists():
            code = random_str(28)
            now = datetime.now()
            email = request.POST['email']
            password = make_password(request.POST['password'])
            username = request.POST['username']
            temporarycode = Passwordresetcodes(email=email , time=now , code= code , username=username )
            temporarycode.save()
          
            message = PMMail(subject= "فعال سازي اکانت امير",sender ="amirhaghparast412@gmail.com" , to = email , text_body="برای فعال کردن اکانت خود روی لینک زیر کلیک کنید:http://http://127.0.0.1:8000/accounts/register/?email={}&code={}".format(email,code),tag = "account request")
            message.send()
           
            
            context = {'message':'ايميل ارسال شد'}
            return render(request,'login.html',context)
        else:
            context = {'message':'این نام کاربری استفاده شده'}
            return render(request,'register.html',context)
    elif 'code' in request.GET:
        email = request.GET['email']
        code =request.GET['code']
        if Passwordresetcodes.objects.filter(code=code).exists():
            new_temp_user = Passwordresetcodes.objects.filter.get(code=code)
            newuser = User.objects.create(username=new_temp_user,password=new_temp_user.password,email=email)
            this_token = random_str(48)
            token = token.objects.create(user=newuser, token=this_token)
            Passwordresetcodes.objects.filter(code=code).delete()
            context = {'message':'اکانت شما فعال شد. توکن شما {} است.'.format(this_token)}
            return render(request,'login.html',context)

        else:
            context= {'message':'این کد فعال سازی معتبر نیست'}
            return render(request,'login.html',context)
    else:
        context = {'message':''}
        return render(request,'register.html',context)
           
@csrf_exempt
def submit_income(request):
    print ('im in submit income')

    this_token = request.POST['token']
    this_user = User.objects.filter(token__token = this_token).get()
    if 'date' not in request.POST:
        date = datetime.now()
    income.objects.create(user = this_user , amount = request.POST['amount'],
                           text = request.POST['text'],date=date)
   
    return JsonResponse({
        'status':'ok'
    },encoder=JSONEncoder)
    
@csrf_exempt
def submit_expense(request):
    print ('im in submit expense')

    this_token = request.POST['token']
    this_user = User.objects.filter(token__token = this_token).get()
    if 'date' not in request.POST:
        date = datetime.now()
    expense.objects.create(user = this_user , amount = request.POST['amount'],
                           text = request.POST['text'],date=date)
   

    return JsonResponse({
        'status':'ok'
    },encoder=JSONEncoder)
