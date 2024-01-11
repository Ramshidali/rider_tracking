#Standard
import os
import string
import random
import random
import string
import requests
from cryptography.fernet import Fernet
#Django
from django.db import models
from django.core.exceptions import ImproperlyConfigured
from django.conf import settings
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.utils.translation import gettext_lazy as _
#Third Party
from random import randint
#Local


def generate_unique_id(size=8, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def generate_form_errors(args,formset=False):
    i = 1
    message = ""
    if not formset:
        for field in args:
            if field.errors:
                message += "\n"
                message += field.label + " : "
                message += str(field.errors)

        for err in args.non_field_errors():
            message += str(err)
    elif formset:
        for form in args:
           
            for field in form:
                if field.errors:
                    message += "\n"
                    message += field.label + " : "
                    message += str(field.errors)
            for err in form.non_field_errors():
                message += str(err)

    message = message.replace("<li>", "")
    message = message.replace("</li>", "")
    message = message.replace('<ul class="errorlist">', "")
    message = message.replace("</ul>", "")
    return message
    

def get_auto_id(model):
    auto_id = 1
    try:
        latest_auto_id =  model.objects.all().order_by("-date_added")[:1]
        if latest_auto_id:
            for auto in latest_auto_id:
                auto_id = auto.auto_id + 1
    except:
        pass
    return auto_id

def randomnumber(n):
    range_start = 10**(n-1)
    range_end = (10**n)-1
    return randint(range_start, range_end)

def paginate(instances, request):
    paginator = Paginator(instances, 20)
    page_number = request.GET.get('page')
    instances = paginator.get_page(page_number)

    return instances

def get_otp(size=4, chars=string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def load_key():
    key = getattr(settings, "PASSWORD_ENCRYPTION_KEY", None)
    if key:
        return key
    else:
        raise ImproperlyConfigured("No configuration  found in your PASSWORD_ENCRYPTION_KEY setting.")

def encrypt_message(message):
    key = load_key()
    encoded_message = message.encode()
    f = Fernet(key)
    encrypted_message = f.encrypt(encoded_message)
    return(encrypted_message.decode("utf-8"))

def decrypt_message(encrypted_message):
    key = load_key()
    f = Fernet(key)
    decrypted_message = f.decrypt(encrypted_message.encode())
    return decrypted_message.decode()

def generate_random_number(length):
    # Define the range of digits
    digits = "0123456789"

    # Generate a random number with the specified length
    random_number = "".join(random.choice(digits) for _ in range(length))
    
    return random_number