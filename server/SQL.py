# -*- coding:utf-8 -*-

from .models import Editor
from .models import Operation

from django.core.paginator import Paginator
from django.core.paginator import PageNotAnInteger
from django.core.paginator import EmptyPage

from django.db.models import Q
from django.db.models import Count
from django.utils import timezone

import datetime
import time

#分页
class JuncheePaginator(Paginator):
      def __init__(self, object_list, per_page, range_num=5, orphans=0, allow_empty_first_page=True):
          Paginator.__init__(self, object_list, per_page, orphans, allow_empty_first_page)
          self.range_num = range_num
  
      def page(self, number):
          self.page_num = int(number)
          return super(JuncheePaginator, self).page(number)
 
      def _page_range_ext(self):
          num_count = 2 * self.range_num + 1
          if self.num_pages <= num_count:
              return range(1, self.num_pages + 1)
          num_list = []
          num_list.append(self.page_num)
          for i in range(1, self.range_num + 1):
              if self.page_num - i <= 0:
                  num_list.append(num_count + self.page_num - i)
              else:
                  num_list.append(self.page_num - i)
 
              if self.page_num + i <= self.num_pages:
                  num_list.append(self.page_num + i)
              else:
                  num_list.append(self.page_num + i - num_count)
          num_list.sort()
          return num_list
      page_range_ext = property(_page_range_ext)

class SQL(object):
    #数据库中Editor表添加记录
    @staticmethod
    def createEditor(editorname, starttime, ip):
        editor = Editor(name=editorname, start_time=int(starttime), client_ip=ip)
        editor.save()
        return editor.id #返回id作为session id
    
    #数据库中Opt表添加记录
    @staticmethod
    def creteOpt(sessionid, cmdstr, exetime):
        #获取editor中的记录
        session = Editor.objects.get(id=int(sessionid))
        if session:
            opt = Operation.objects.create(session_id=session, cmd=cmdstr, time = int(exetime))
            opt.save()
            return "success"
        else:
            return "no session"

    @staticmethod
    def updateEditor(sessionid, stoptime, exitcode):
        session = Editor.objects.get(id=int(sessionid))
        if session:
            session.exit_code = exitcode
            session.stop_time = int(stoptime)
            session.save()
            return "success"
        else:
            return "no session"

    @staticmethod
    def updateEditorAtt(sessionid):
        session = Editor.objects.get(id=int(sessionid))
        if session:
            session.attachment = True
            session.save()
            return "success"
        else:
            return "no session"
        
    @staticmethod
    def getAllEditor():
        return Editor.objects.all().exclude(name="")
    
    @staticmethod
    def getEditorOpt(sessionid):
        return Editor.objects.all().get(id=int(sessionid)).editors.all()
        
    #获取name列表

    @staticmethod
    def getAllEditorName(currPage = None):
        if currPage != None:
            return SQL.paging(SQL.getAllEditor().values('name').distinct(), 20, currPage)
        else:
            return SQL.getAllEditor().values('name').distinct()
        
    @staticmethod
    def getAllEditorUserByName(editorname, currPage = None):
        if currPage == None:
            return SQL.getAllEditor().filter(name=editorname)
        else:
            return SQL.paging(SQL.getAllEditor().filter(name=editorname).order_by('-start_time'), 20, currPage)

    @staticmethod
    def getEditorNameByIP(clientIP, currPage):
        return SQL.paging(SQL.getAllEditor().filter(client_ip=clientIP).values('name').distinct(), 20, currPage)
    
    #获取user列表
    @staticmethod
    def getEditorUserByIP(clientIP, editorname , currPage = None):
        if currPage == None:
            return SQL.getAllEditor().filter(Q(client_ip=clientIP), Q(name=editorname))
        else:
            return SQL.paging(SQL.getAllEditor().filter(Q(client_ip=clientIP), Q(name=editorname)).order_by('-start_time'), 20, currPage)

    @staticmethod
    def getEditorNameByDump(dump, currPage):
        if dump == "0":
            return SQL.paging(SQL.getAllEditor().filter(exit_code="0").values('name').distinct(), 20, currPage)
        else:
            return SQL.paging(SQL.getAllEditor().exclude(exit_code="0").values('name').distinct(), 20, currPage)
            
    @staticmethod
    def getEditorUserByDump(dump, editorname , currPage = None):
        if currPage == None:
            if dump == "0":
                return SQL.getAllEditor().filter(Q(exit_code="0"), Q(name=editorname))
            else:
                return SQL.getAllEditor().filter(~Q(exit_code="0"), Q(name=editorname))
        else:
            if dump == "0":
                return SQL.paging(SQL.getAllEditor().filter(Q(exit_code="0"), Q(name=editorname)).order_by('-start_time'), 20, currPage)
            else:
                return SQL.paging(SQL.getAllEditor().filter(~Q(exit_code="0"), Q(name=editorname)).order_by('-start_time'), 20, currPage)
            
    @staticmethod
    def getEditorNameByTime(starttime, endtime, currPage):
        startDate = time.mktime(time.strptime(starttime + "-0", '%Y-%m-%d-%H')) - time.timezone
        endDate = time.mktime(time.strptime(endtime + "-23-59", '%Y-%m-%d-%H-%M')) - time.timezone
        return SQL.paging(SQL.getAllEditor().filter(start_time__range=(startDate, endDate)).values('name').distinct(), 20, currPage)
    
    @staticmethod
    def getEditorByTime(starttime, endtime):
        startDate = time.mktime(time.strptime(starttime + "-0", '%Y-%m-%d-%H')) - time.timezone
        endDate = time.mktime(time.strptime(endtime + "-23-59", '%Y-%m-%d-%H-%M')) - time.timezone
        return SQL.getAllEditor().filter(start_time__range=(startDate, endDate))

    @staticmethod
    def getEditorUserByTime(starttime, endtime, editorname, currPage = None):
        startDate = time.mktime(time.strptime(starttime + "-0", '%Y-%m-%d-%H')) - time.timezone
        endDate = time.mktime(time.strptime(endtime + "-23-59", '%Y-%m-%d-%H-%M')) - time.timezone
        if currPage == None:
            return SQL.getAllEditor().filter(Q(start_time__range=(startDate, endDate)), Q(name=editorname))
        else:
            return SQL.paging(SQL.getAllEditor().filter(Q(start_time__range=(startDate, endDate)), Q(name=editorname)).order_by('-start_time'), 20, currPage)

    @staticmethod
    def getOptByID(eid, currPage):
        return SQL.paging(SQL.getEditorOpt(eid), 20, currPage)

    @staticmethod
    def paging(obj, pages, currPage):
        paginator = JuncheePaginator(obj, pages)
        try:
            temp = paginator.page(currPage)
        except PageNotAnInteger:
            temp = paginator.page(1)
        except EmptyPage:
            temp = paginator.page(paginator.num_pages)
        return temp

    @staticmethod
    def getDetailTimes(name, success, dump, obj = None):
        #print obj
        if obj == None:
            obj = SQL.getAllEditorUserByName(name)
        days = getDays(obj.values('start_time').distinct())
        for day in days:
            success.append(obj.filter(Q(start_time__gte=day, start_time__lte=day+86400), Q(exit_code="0")).count())
            dump.append(obj.filter(Q(start_time__gte=day, start_time__lte=day+86400), ~Q(exit_code="0")).count())
        return days
    
    @staticmethod
    def getAllTimes(name, obj=None):
        if obj == None:
            obj = SQL.getAllEditorUserByName(name)
        return obj.count()

    @staticmethod
    def getSuccessTimes(name, obj=None):
        if obj == None:
            obj = SQL.getAllEditorUserByName(name)
        return obj.filter(exit_code="0").count()

    @staticmethod
    def getDumpTimes(name, obj=None):
        if obj == None:
            obj = SQL.getAllEditorUserByName(name)
        return obj.exclude(exit_code="0").count()
    
    @staticmethod
    def getMaxIPTimes(obj=None):
        if obj == None:
            obj = SQL.getAllEditor()
        ipObj = obj.values("client_ip").annotate(ip_times=Count('client_ip')).all().order_by('-ip_times')
        if len(ipObj) <= 0:
            return
        ip = ipObj[0]["client_ip"] 
        ipObj = obj.filter(client_ip=ip).values("name", "client_ip").annotate(times=Count('name')).all().order_by('-times')
        return ipObj


def getZeroStamp(stamp):
    #print stamp
    #print int(stamp["start_time"]) - int(stamp["start_time"]) % 86400 + time.timezone
    return int(stamp["start_time"]) - int(stamp["start_time"]) % 86400 + time.timezone

def getDays(starttimes):
    days = set()
    for starttime in starttimes:
        zero_time = getZeroStamp(starttime)
        days.add(zero_time)
    day_list = list(days)
    day_list.sort()
    return day_list