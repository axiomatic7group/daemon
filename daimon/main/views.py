from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, JsonResponse
from django.views import View
from django.utils import timezone
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, PasswordResetForm
from django.views.decorators.csrf import csrf_exempt

import pandas as pd
import json, re

from dateutil.relativedelta import relativedelta
from datetime import datetime, date, timedelta

def form_to_json_schema(form):
    schema = {}
    
    for name, field in form.fields.items():    
        field_data = {}
        
        if hasattr(field, 'choices') and field.choices:
            field_data['choices'] = [{'option': str(c[1])} for c in field.choices]

        schema[name] = field_data
    return schema

class authenticate_users(View):
    def get(self, request):
        user_auth_form = AuthenticationForm(request.GET or None)

        context = {'user_auth_form':user_auth_form}
        return render(request, './login.html', context)
    
    def post(self, request):
        user_auth_form = AuthenticationForm(data=request.POST)

        if user_auth_form.is_valid():
            username = user_auth_form.cleaned_data.get('username')
            password = user_auth_form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                
                return redirect('/pm/projects/')

        context = {'user_auth_form':user_auth_form}
        return render(request, './login.html', context)
    
    def get_api(self):
        json_form = {'message':'Welcome! Please make sure your response follows the format provided below.',
                     'format':{'login': {'username':'new_user',
                                         'password':'super_secure_password'}
                     }}
        return JsonResponse(json_form)
       
    @csrf_exempt
    def post_api(request):
        data = json.loads(request.body.decode('utf-8'))
        login_data = data['login']
        username = login_data['username']
        password = login_data['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            session_id = request.session.session_key
            data = {'message':'user has been authenticated.',
                    'session_id':session_id}
            print(data)
            return JsonResponse(data)

        else:
            data = {'message':'An error has occured, please ensure your request follows the format below.',
                    'format':{'login': {'username':'new_user',
                                         'password':'super_secure_password'}}}
            print(data)
            return JsonResponse(data)

