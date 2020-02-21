from django.shortcuts import render,loader,redirect
from django import forms
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.sessions.models import Session
from django.db import models, connection
from django.core import signing
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger
from django.urls import reverse
from django.template import RequestContext
from django.core.mail import send_mail
from django.contrib.auth import authenticate, login, logout
# from django.contrib.auth.models import User
from django.core.cache import cache
from django.http import HttpResponseRedirect,HttpResponse,Http404
from .models import registration
from .forms import Tool_ASIN
from . import forms
from . import models
import json
from .Toolbox import Toolbox
import sweetify

tlbx = Toolbox()
#tlbx.startLogger()
tlbx.establish_PGSQL()

from .models import User


def tool_asin_view(request):
    if request.method == 'POST':
        form = Tool_ASIN(request.POST)
        if form.is_valid():
            asin = form.cleaned_data['asin']
            print(80*"*")
            print(asin)
            print(80*"*")
    form = Tool_ASIN()
    return render(request, 'tool_asin.html', {'form': form})

def error_404(request):
    log_msg = "404 - not found"
    tlbx.multiLogger(log_msg, level = 2)
    return render(request,'error_404.html')

def requestreset(request):
    print("* * Loading request reset")
    return render(request,'requestreset.html')

def reset(request):
    return render(request,'reset.html')

def inactive(request):
    ''' Displays the page for an inactive user  '''
    print("* * Loading inactive")
    # - If the session credentials are valid
    if 'user' in request.session and request.session['user'] is not None:
        try:
            # - If the user is actually active, send to profile
            user_obj = User.objects.get(username=request.session['user'])
            if user_obj.is_active:
                return redirect("../account_dashboard/")
            else:
                # - If the user is confirmed inactive, show the inactive page
                return render(request,'inactive.html')
        except User.DoesNotExist:
            # - If the user is not found at all, send to register
            print("* * * user does not exist")
            return redirect("../register/")
    else:
        # - If no session credentials exist, send to login
        return redirect("../login/")
    # - If nothing worked (??) render inactive page
    return render(request,'inactive.html')

def index(request):
    '''    Get to registration form signup    '''
    return redirect("../login/",context)


def helper_checkLogins(request, renderpage, context_param = {}):
    """
        Runs a generic check against all requests to assure that 
        the user is logged in.
    """
    log_msg = "Request is: {request}".format(request = request)
    tlbx.multiLogger(log_msg, level=1)
    try:
        user_pk = User.objects.get(email=request.session['user']).id
        log_msg = "User is logged in as ID: {user_pk}".format(user_pk = user_pk)
        tlbx.multiLogger(log_msg)
    except:
        log_msg = "User is not logged in.  Redirecting.."
        tlbx.multiLogger(log_msg)
        return redirect("../login/")
   
    # - If session is valid, get object & check if active
    try:
        user_obj = User.objects.get(id=user_pk)
        # - If inactive, send to inactive page
        if user_obj.is_active == False:
            log_msg = "Inactive user cannot access the site."
            tlbx.multiLogger(log_msg, level = 2)
            return redirect("../inactive/")
    # - If user is missing altogether, send to login
    except User.DoesNotExist:
        log_msg = "User does not exist"
        tlbx.multiLogger(log_msg, level = 2)
        return redirect("../login/")

    if not request.session._session_key:
        request.session.save()
    context = context_param
    context['status'] = 200
    context['username'] = str(user_obj).upper()
    #log_msg = "Context is: {context}".format(context = context)
    #tlbx.multiLogger(log_msg)
    return render(request,renderpage,context)

def marketplace_amazon(request):
    sql_query = """SELECT
            case_type
            , amazoncaseid
            , amazonorderid
            , requestedamount
            , amount_total
            , quantity_reimbursed_cash
            , quantity_reimbursed_inventory
            , quantity_reimbursed_total
            , reason
        FROM case_results"""
    tlbx.PGSQL_DICT_CURSOR.execute(sql_query)
    context = {}
    context['cases'] = tlbx.PGSQL_DICT_CURSOR.fetchall()
    return helper_checkLogins(request, "marketplace_amazon.html", context)

def marketplace_ebay(request):
    return helper_checkLogins(request, "marketplace_ebay.html")

def marketplace_groupon(request):
    return helper_checkLogins(request, "marketplace_groupon.html")

def marketplace_newegg(request):
    return helper_checkLogins(request, "marketplace_newegg.html")

def marketplace_rakuten(request):
    return helper_checkLogins(request, "marketplace_rakuten.html")

def marketplace_walmart(request):
    return helper_checkLogins(request, "marketplace_walmart.html")

def account_invoices(request):
    return helper_checkLogins(request, "account_invoices.html")
    
def account_settings(request):
    return helper_checkLogins(request, "account_settings.html")

def main_subpage_1(request):
    return helper_checkLogins(request, "main_subpage_1.html")

def main_subpage_2(request):
    return helper_checkLogins(request, "main_subpage_2.html")

def main_subpage_3(request):
    return helper_checkLogins(request, "main_subpage_3.html")

def account_dashboard(request):
    return helper_checkLogins(request, "account_dashboard.html")

def courier_fedex(request):
    return helper_checkLogins(request, "courier_fedex.html")

def courier_ups(request):
    return helper_checkLogins(request, "courier_ups.html")

def courier_usps(request):
    return helper_checkLogins(request, "courier_usps.html")

def courier_dhl(request):
    return helper_checkLogins(request, "courier_dhl.html")

def user_logout(request):
    '''Logs the user out by removing all traces of their login'''
    print("* * Loading user logout")
    logout(request)
    request.session['user']=None
    for x in request.COOKIES.keys():
        del x
    args = {}
    print(request.session['user'])
    return redirect("../login/")


def register_user(request):
    '''Registers a new user'''
    print("* * Loading Register user")
    tlbx = Toolbox()
    context = {}
    if request.user.is_authenticated:
        try:
            user_obj = User.objects.get(email=request.session['user'])
            if user_obj.is_active:
                return redirect("../account_dashboard/")
            else:
                return redirect("../inactive/")
        except User.DoesNotExist:
            return redirect("../logout/")

    # - On GET request, respond with the plain page
    if request.method != 'POST':
        return render(request, "register.html")
    if 'user' in request.session and request.session['user'] is not None:
        try:
            user_obj = User.objects.get(email=request.session['user'])
            if user_obj.is_active:
                return redirect("../account_dashboard/")
            else:
                return redirect("../inactive/")
        except User.DoesNotExist:
            print("user doesn't exist.")
    try:
        user_email_lowercase = str(request.POST['email']).lower()
        user_obj = User.objects.get(email=user_email_lowercase)
        print(user_obj)
        print("* * user already exists!")
        sweetify.error(request, 'User already exists!'
            , text='Login to your account here.'
            , persistent='Got it')
        return redirect("../login/")
    except:
        print('passed')
    form = forms.RegisterUser(data=request.POST)
    # - fail if form is invalid
    if form.is_valid():
        form.save()#if it is, save it
        user_email_lowercase = str(request.POST['email']).lower()
        user_obj = User.objects.get(email=user_email_lowercase)
        # user_obj.username = user_email_lowercase
        user_obj.save()
        login(request, user_obj)
        print(user_obj.email)
        request.session.update({'user':user_obj.email})
        #return HttpResponseRedirect("/account_dashboard/",context)
        print("* * * sending to dashboard")
        return redirect("../account_dashboard/", context)
    else:
        print(80*"*")
        print(form.errors)
        sweetified_resp = tlbx.sweetify_errors(str(form.errors))
        sweetify.error(request, 'Cannot create user!'
            , text="Please fix the following issues\n----------------------------------------\n{}".format(sweetified_resp)
            , persistent='Got it')
        return render(request, "register.html", context)


def user_login(request):
    # - If user is already logged in, redirect
    print("* * Loading user login")
    if request.user.is_authenticated:
        try:
            user_obj = User.objects.get(email=request.session['user'])
            if user_obj.is_active:
                return redirect("../account_dashboard/")
            else:
                return redirect("../inactive/")
        except User.DoesNotExist:
            return redirect("../logout/")

    # - If no session data exists & no post data exists, show plain page
    if request.method!="POST":
        return render(request,"login.html")

    current_email       = request.POST.get('email').lower()
    current_password    = request.POST.get('password1')
    print("current_email is {}".format(current_email))
    if current_email == '':
        print('email cannot be blank')
        sweetify.error(request, 'Cannot log in!'
            , text="The user field cannot be blank"
            , persistent='Got it')
        return redirect("../login/")

    if current_password == '':
        print('password cannot be blank')
        sweetify.error(request, 'Cannot log in!'
            , text="The password field cannot be blank"
            , persistent='Got it')
        return redirect("../login/")

    try:
        tmp = User.objects.get(email=current_email)
    except User.DoesNotExist:
        # messages.add_message(request,messages.ERROR,"Invalid credentials")
        # return redirect("../register/")
        print(" & & & user does not exist!")
        sweetify.error(request, 'User does not exist!'
            , text="The user does not exist.\nRegister an account here"
            , persistent='Got it')
        return redirect("../register/")

    user_obj = authenticate(email=current_email, password=current_password)

    if user_obj is None:
        sweetify.error(request, 'Cannot log in!'
            , text="Incorrect password"
            , persistent='Got it')
        return redirect("../login/")
    else:
        request.session.create()
        request.session['user']=str(user_obj)
        request.session.modified = True
        login(request,user_obj)
        print("logged in with {}".format(user_obj))
        return redirect("../account_dashboard/")

def disable(request,user_name):  
    user_id = User.objects.get(username=user_name).id
    reg_user = registration.objects.get(username=user_id)
    if request.method == "POST":
        user = authenticate(username=request.POST.get('username'),password=request.POST.get('password'))
        if user is not None:
            if reg_user.disabled:
                reg_user.disabled=False
            else:
                reg_user.disabled=True
            reg_user.save() 
            return HttpResponse(json.dumps({"status":200,"disabled":reg_user.disabled}),content_type="application/json")
        else:
            return HttpResponse(json.dumps({"status":400,"disabled":reg_user.disabled}),content_type="application/json")
        return HttpResponse("Some random stuff")

    return HttpResponse("Account was disabled")

def page_not_found(request):
    return render(request, '404.html')

def page_500(request):
    return HttpResponse("5000")

def content(request):
    return render(request, 'content.html')
