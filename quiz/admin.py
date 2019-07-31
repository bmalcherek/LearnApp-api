from __future__ import unicode_literals

from django.contrib import admin
from .models import Question, Collection, MyCollections, MyQuestions

admin.site.register(Question)
admin.site.register(Collection)
admin.site.register(MyCollections)
admin.site.register(MyQuestions)
