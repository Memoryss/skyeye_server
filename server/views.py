from django.shortcuts import render
from django.http import HttpResponse
from django.utils import timezone
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import simplejson as json

from SQL import *

import logging
import os
import base64
import zlib

logger = logging.getLogger(__name__)

class Session(object):
    @staticmethod
    def create_session(request):
        if request.method == 'POST':
            logger.info("create session")
            req = json.loads(request.body)
            sessionid = SQL.createEditor(req["editor"], req["start_time"], req["client_ip"])
            return HttpResponse(sessionid)

    @staticmethod
    def recv_operator(request, sessionid):
        if request.method == 'POST':
            logger.info(str(sessionid) + ":create opt")
            req = json.loads(request.body)
            result = SQL.creteOpt(sessionid, req["cmd"], req["time"])
            return HttpResponse(result)

    @staticmethod
    def recv_stop(request, sessionid):
        if request.method == 'POST':
            logger.info(str(sessionid) + ":stop")
            req = json.loads(request.body)
            result = SQL.updateEditor(sessionid, req["stop_time"], req["exit_code"])
            return HttpResponse(result)
    
    @staticmethod
    def recv_attachment(request, sessionid):
        if request.method == 'POST':
            req = json.loads(request.body)
            result = SQL.updateEditorAtt(sessionid)
            if result == "success":
                print req
                basedir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                filepath = os.path.join(basedir, 'attachments', str(sessionid))
                handle_uploaded_file(req['name'], req['content'], filepath)
            return HttpResponse(result)

def handle_uploaded_file(content, filename, filepath):
    if not os.path.exists(filepath):
        os.makedirs(filepath)
    filecontent = base64.b64decode(content)
    filecontent = zlib.decompress(filecontent)
    open(os.path.join(filepath, filename), "wb").write(filecontent)

def get_file_names(directory, parentdir):
    contents = os.listdir(directory)
    files = list()
    for item in contents:
        if os.path.isfile(os.path.join(directory, item)):
            item = os.path.join(parentdir, item)
            files.append(item)
        else:
            tempdir = os.path.join(directory, item)
            tempfiles = get_file_names(tempdir, os.path.basename(tempdir))
            files += tempfiles
    return files