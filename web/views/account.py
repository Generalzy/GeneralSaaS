from django.shortcuts import render, HttpResponse, redirect
from django.conf import settings
from web.forms import RegisterForm, SmsForm, LoginForm, CodeLoginForm
from django.http import JsonResponse
from utils.response import ApiResponse
from django.core.cache import cache
from web import models
from utils.pacture import get_png
from libs.tencent.sends import send_message
from uuid import uuid4
from datetime import datetime
import random


# Create your views here.

def register(request):
    if request.method == 'GET':
        form = RegisterForm()
        return render(request, 'register.html', locals(), status=200)
    elif request.method == 'POST':
        res = ApiResponse()
        form = RegisterForm(data=request.POST)
        if form.is_valid():
            instance = form.save()
            # 产生交易记录
            price_instance = models.PricePolicy.objects.filter(title='个人免费版', category=1).first()
            models.Transaction.objects.create(
                status=2,
                order=str(uuid4()),
                count=0,
                user=instance,
                price_policy=price_instance,
                price=0,
                create_datetime=datetime.now()
            )
            res.url = '/smslogin/'
            return JsonResponse(res.data)
        else:
            res.errors = form.errors
            res.code = 0
            res.msg = '失败'
            return JsonResponse(res.data)


def sms(request):
    if request.method == 'POST':
        res = ApiResponse()
        form = SmsForm(data=request.POST)
        phone = request.POST.get('phone')
        if form.is_valid():
            sms_code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
            send_message(phone, sms_code)
            cache.set(f'{settings.PHONE_CACHE_KEY}{phone}', sms_code, 60)
            return JsonResponse(res.data)
        else:
            res.msg = form.errors
            res.code = 0
            return JsonResponse(res.data)
    else:
        return None


def sms_login(request):
    if request.method == 'GET':
        form = LoginForm()
        return render(request, 'login.html', {'form': form})
    elif request.method == 'POST':
        res = ApiResponse()
        form = LoginForm(data=request.POST)
        phone = request.POST.get('phone')
        if form.is_valid():
            user_obj = models.UserInfo.objects.filter(phone=phone).first()
            request.session['username'] = user_obj.username
            request.session.set_expiry(60 * 60 * 24 * 7)
            res.url = '/index/'
            return JsonResponse(res.data)
        else:
            res.code = 0
            res.msg = form.errors
        return JsonResponse(res.data)


def code(request):
    png_code, png = get_png()
    request.session['code'] = png_code
    request.session.set_expiry(60)
    return HttpResponse(png)


def login(request):
    if request.method == 'GET':
        form = CodeLoginForm(request)
        return render(request, 'codeLogin.html', {'form': form})
    elif request.method == 'POST':
        form = CodeLoginForm(data=request.POST, request=request)
        username = request.POST.get('username')
        if form.is_valid():
            user_obj = models.UserInfo.objects.filter(username=username).first()
            request.session['username'] = user_obj.username
            request.session.set_expiry(60 * 60 * 24 * 7)
            return redirect('index')
        else:
            return render(request, 'codeLogin.html', {'form': form})


def logout(request):
    request.session.flush()
    return redirect('index')
