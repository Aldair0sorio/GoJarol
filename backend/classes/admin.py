from django.contrib import admin

from .models import ClassAnnouncement, ClassChallenge, Classroom, Enrollment

admin.site.register(Classroom)
admin.site.register(Enrollment)
admin.site.register(ClassAnnouncement)
admin.site.register(ClassChallenge)
