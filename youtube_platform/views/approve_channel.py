from django.shortcuts import redirect

import httplib2
import os
import re
import sys

from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow

def oauth2callback(request): 

    return redirect('/')

def approve_channel(request): 
 
    return redirect('https://accounts.google.com/o/oauth2/auth?client_id=1095315896769-nikvtj3u6q39fijic8h4ljuhjlp9fn1j.apps.googleusercontent.com&redirect_uri=http://platform.adytools.com/oauth2callback&response_type=code&scope=https://www.googleapis.com/auth/youtube')





