from __future__ import unicode_literals
from django.utils import timezone
from django.db import models

import os
import datetime

class Editor(models.Model):
    def __unicode__(self):
        return self.name
    id = models.AutoField(primary_key=True)  #session 
    name = models.CharField(max_length=200) # editor name 
    start_time = models.IntegerField()
    stop_time = models.IntegerField(default=0)
    client_ip = models.CharField(max_length=200)
    exit_code = models.CharField(max_length=50)
    attachment = models.BooleanField(default=False)

class Operation(models.Model):
    def __unicode__(self):
        return self.cmd
    session_id = models.ForeignKey(Editor, on_delete=models.CASCADE, related_name="editors")
    id = models.AutoField(primary_key=True)
    cmd = models.CharField(max_length=10000)
    time = models.IntegerField()
