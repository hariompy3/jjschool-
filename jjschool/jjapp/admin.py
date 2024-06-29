from django.contrib import admin
from .models import *

admin.site.register(CustomUser)
admin.site.register(Teacher)
admin.site.register(Student)
admin.site.register(Exam)
admin.site.register(TeacherSubjectAssignment)
admin.site.register(Classroom)
admin.site.register(Grade)
admin.site.register(Subject)
admin.site.register(Notification)
admin.site.register(Attendance)

