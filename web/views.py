# -*- coding:utf-8 -*-

import sys
import os
sys.path.append("..")

from django.shortcuts import render
from django.http import HttpResponse
from django.core.serializers.json import DjangoJSONEncoder
from django.core.serializers import serialize
from django.db.models import Q
import logging
import json
import operator

from server.SQL import *

logger = logging.getLogger(__name__)

#序列化
class DjangoOverRideJSONEncoder(DjangoJSONEncoder):
    """
    JSONEncoder subclass that knows how to encode date/time and decimal types.
    """
    def default(self, o):
        # See "Date Time String Format" in the ECMA-262 specification.
        if isinstance(o, datetime.datetime):
            r = o.isoformat(' ')
            if o.microsecond:
                r = r[:23] + r[26:]
            if r.endswith('+00:00'):
                r = r[:-6]
            return r
        elif isinstance(o, datetime.date):
            return o.isoformat(' ')
        elif isinstance(o, datetime.time):
            if is_aware(o):
                raise ValueError("JSON can't represent timezone-aware times.")
            r = o.isoformat(' ')
            if o.microsecond:
                r = r[:12]
            return r
        elif isinstance(o, decimal.Decimal):
            return str(o)
        else:
            return super(DjangoOverRideJSONEncoder, self).default(o)

#展示
class Show(object):
    @staticmethod
    def init(request):
        logger.info("init show")
        currPage = (request.GET.get('namepage') and request.GET.get('namepage') or 1)
        editorName = Show.initName(currPage)
        if (len(editorName.object_list) <= 0):
            logger.warning("No Data")
            return render(request, 'index.html')
        
        ename = editorName.object_list[0]
        currPage = (request.GET.get('userpage') and request.GET.get('userpage') or 1)
        editorUser = Show.initUser(ename, currPage)

        eid = -1
        opt = None
        if (len(editorUser) > 0):
            eid = editorUser[0].id
            currPage = (request.GET.get('optpage') and request.GET.get('optpage') or 1)
            opt = Show.initOpt(eid, currPage)
        print ename
        return render(request, 'index.html', {'eidtorname':editorName, 'editorUser':editorUser, 'opt':opt, 'ename':ename, 'eid':eid})

    @staticmethod
    def initFile(request):
        logger.info("init show file")
        editor = SQL.getAllEditor().filter(id=request.GET.get('id'))
        basedir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        files = get_file_names(os.path.join(basedir, 'attachment', str(editor[0].id)), '')
        return render(request, 'download.html', {'ename':editor[0].name, 'directory_files':files, 'eid':editor[0].id})
        

    @staticmethod
    def initName(currPage):
        logger.debug("namepage:" + str(currPage))
        return SQL.paging(SQL.getAllEditor().values('name').distinct(), 20, currPage)
    
    @staticmethod
    def initUser(editorname, currPage):
        logger.debug("userpage:" + str(currPage))
        return SQL.paging(SQL.getAllEditor().filter(name=editorname), 20, currPage)
    
    @staticmethod
    def initOpt(id, currPage):
        logger.debug("optpage:" + str(currPage))
        return SQL.paging(SQL.getEditorOpt(id), 20, currPage)

    @staticmethod
    def chart(request):
        return render(request, 'chart.html')

class Search(object):

    @staticmethod
    def searchName(request):
        logger.info('search name list')
        editorName = {}
        if request.GET.get('ip') != None:
            editorName = SQL.getEditorNameByIP(request.GET.get('ip'), request.GET.get('namepage'))
        elif request.GET.get('dump') != None:
            editorName = SQL.getEditorNameByDump(request.GET.get('dump'), request.GET.get('namepage'))
        elif request.GET.get('starttime') != None:
            editorName = SQL.getEditorNameByTime(request.GET.get('starttime'), request.GET.get('endtime'), request.GET.get('namepage'))
        else:
            editorName = SQL.getAllEditorName(request.GET.get('namepage'))
        
        if len(list(editorName)) <= 0:
            logger.warning('no data')
            return HttpResponse(json.dumps({}))
        
        editorname_json = json.dumps(list(editorName))
        j = json.loads(editorname_json)
        if len(j) > 0:
            j[0]["has_previous"] = editorName.has_previous()
            j[0]['has_next'] = editorName.has_next()
            j[0]['page_rang'] = editorName.paginator.page_range_ext
        return HttpResponse(json.dumps(j))
    @staticmethod
    def searchUser(request):
        editor = {}
        if (request.GET.get('userpage') == None):
            if request.GET.get('ip') != None:
                editor = SQL.getEditorUserByIP(request.GET.get('ip'), request.GET.get('name'), request.GET.get('namepage'))
            elif request.GET.get('dump') != None:
                editor = SQL.getEditorUserByDump(request.GET.get('dump'), request.GET.get('name'))
            elif request.GET.get('starttime') != None:
                editor = SQL.getEditorUserByTime(request.GET.get('starttime'), request.GET.get('endtime'), request.GET.get('name'))
            else:
                editor = SQL.getAllEditorUserByName(request.GET.get('name'))
            user_json = serialize("json", editor, cls=DjangoOverRideJSONEncoder)
            return HttpResponse(user_json)
        else:
            if request.GET.get('ip') != None:
                editor = SQL.getEditorUserByIP(request.GET.get('ip'), request.GET.get('name'), request.GET.get('userpage'))
            elif request.GET.get('dump') != None:
                editor = SQL.getEditorUserByDump(request.GET.get('dump'), request.GET.get('name'), request.GET.get('userpage'))
            elif request.GET.get('starttime') != None:
                editor = SQL.getEditorUserByTime(request.GET.get('starttime'), request.GET.get('endtime'), request.GET.get('name'), request.GET.get('userpage'))
            else:
                editor = SQL.getAllEditorUserByName(request.GET.get('name'), request.GET.get('userpage'))

            user_json = serialize("json", editor, cls=DjangoOverRideJSONEncoder)
            j = json.loads(user_json)
            if len(j) > 0:
                j[0]["has_previous"] = editor.has_previous()
                j[0]['has_next'] = editor.has_next()
                j[0]['page_rang'] = editor.paginator.page_range_ext
            return HttpResponse(json.dumps(j))

    @staticmethod
    def searchOpt(request):
        opt = SQL.getOptByID(request.GET.get('id'), request.GET.get('optpage'))
        opt_json = serialize("json", opt, cls=DjangoOverRideJSONEncoder)
        j = json.loads(opt_json)
        if len(j) > 0:
            j[0]["has_previous"] = opt.has_previous()
            j[0]['has_next'] = opt.has_next()
            j[0]['page_rang'] = opt.paginator.page_range_ext
        return HttpResponse(json.dumps(j))
    '''
    @staticmethod
    def searchAllChart(request):
        editorName = SQL.getAllEditorName()
        editorData = {}
        for editor in editorName:
            data_json = serialize("json", SQL.getAllEditorUserByName(editor["name"]), cls=DjangoOverRideJSONEncoder, fields=('start_time', 'exit_code'))
            print data_json
            editorData[editor["name"]] = data_json
        return HttpResponse(json.dumps(editorData))
    '''
    
    @staticmethod
    def searchDetailChart(request):
        editorName = SQL.getAllEditorName()
        editorData = {}
        for editor in editorName:
            if editor["name"] == "":
                continue
            data = []
            success = []
            dump = []
            obj = None
            if request.GET.get('starttime') != None:
                obj = SQL.getEditorUserByTime(request.GET.get('starttime'), request.GET.get('endtime'), editor["name"])
            days = SQL.getDetailTimes(editor["name"], success, dump, obj)
            if len(days) <= 0:
                continue
            data.append(days)
            data.append(success)
            data.append(dump)
            editorData[editor["name"]] = data
        editor_json = json.dumps(editorData)
        return HttpResponse(editor_json)
    
    @staticmethod
    def searchTimes(request):
        editorName = SQL.getAllEditorName()
        editorData = {}
        editorTimes = {}
        if request.GET.get('type') == "total":
            for editor in editorName:
                if editor["name"] == "":
                    continue

                obj = None
                if request.GET.get('starttime') != None:
                    obj = SQL.getEditorUserByTime(request.GET.get('starttime'), request.GET.get('endtime'), editor["name"])
                editorTimes[editor["name"]] = SQL.getAllTimes(editor["name"], obj)
        elif request.GET.get('type') == "success":
            for editor in editorName:
                if editor["name"] == "":
                    continue
                obj = None
                if request.GET.get('starttime') != None:
                    obj = SQL.getEditorUserByTime(request.GET.get('starttime'), request.GET.get('endtime'), editor["name"])
                editorTimes[editor["name"]] = SQL.getSuccessTimes(editor["name"], obj)
        else:
            for editor in editorName:
                if editor["name"] == "":
                    continue
                obj = None
                if request.GET.get('starttime') != None:
                    obj = SQL.getEditorUserByTime(request.GET.get('starttime'), request.GET.get('endtime'), editor["name"])
                editorTimes[editor["name"]] = SQL.getDumpTimes(editor["name"], obj)
        #editorTimes_sort = sorted(editorTimes.items(), key=operator.itemgetter(1))
        #print editorTimes_sort
        editor_json = json.dumps(editorTimes)
        return HttpResponse(editor_json)
    
    @staticmethod
    def searchIPTimes(request):
        obj = None
        if request.GET.get('starttime') != None:
            obj = SQL.getEditorByTime(request.GET.get('starttime'), request.GET.get('endtime'))
        ipObj = SQL.getMaxIPTimes(obj)
        if ipObj == None:
            return HttpResponse(json.dumps({}))
        data_json = json.dumps(list(ipObj))
        return HttpResponse(data_json)

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