import hashlib, time, random

from datetime import datetime

from django.shortcuts import render
from django.http import Http404
from django.contrib.auth import logout
from django.template import RequestContext
from django import forms
from django.http import HttpResponseRedirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required

from inboxen.models import Tag, Domain, Alias

def register(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect("/accounts/profile")

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            return HttpResponseRedirect('/profile')
    else:
        form = UserCreationForm()
    
    context = {
        "form":form,
        "page":"Register",
    }

    return render(request, "register.html", context, context_instance=RequestContext(request))

@login_required
def add_alias(request):
    
    if request.method == "POST":
        alias = request.POST["alias"]
        domain = Domain.objects.get(domain=request.POST["domain"])
        tags = request.POST["tag"].split(",")
        
        new_alias = Alias(alias=alias, domain=domain, user=request.user, created=datetime.now())
        new_alias.save()
        
        for i, tag in enumerate(tags):
            tags[i] = Tag(tag=tag)
            tags[i].alias = new_alias
            tags[i].save()
 
        return HttpResponseRedirect("/accounts/profile")

    alias = "%s-%s" % (time.time(), request.user.username) 
    domains = Domain.objects.all()
    
    alias = ""
    count = 0
    while not alias and count < 10:
        alias = "%s-%s" % (time.time(), request.user.username)
        alias = hashlib.sha1(alias).hexdigest()[:count+5]
        try:
            Alias.objects.get(alias=alias)
            alias = ""
            count += 1
        except:
            pass
    context = {
        "page":"Add Alias",
        "domains":domains,
        "alias":alias,
    }
    
    return render(request, "add_alias.html", context)

@login_required
def settings(request):
   
    context = {
        "page":"Settings",
    }

    return render(request, "settings.html", context)

@login_required
def logout_user(request):
    
    logout(request)
    return HttpResponseRedirect("/")

@login_required
def inbox(request, inbox, domain):
    context = {
        "page":inbox,
    }
    return render(request, "inbox.html", context)

@login_required
def profile(request):

    try:
        aliases = Alias.objects.filter(user=request.user).order_by('created')
    except:
        raise
        aliases = []

    tags = {}
    try:
        for alias in aliases:
            tag = Tag.objects.filter(alias=alias)
            tags[alias] = ", ".join([t.tag for t in tag])
    except:
        pass

    context = {
        "page":"Profile",
        "aliases":aliases,
        "tags":tags,
    }
    
    return render(request, "profile.html", context)

def login(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect("/accounts/profile")

    context = {
        "page":"Login",
    } 

    return render(request, "login.html", context)

def contact(request):
    context ={
        "page":"Contact",
    }

    return render(request, "contact.html", context)

def home(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect("/accounts/profile")

    context = {
        "page":"Home",
    }

    return render(request, "index.html", context)
