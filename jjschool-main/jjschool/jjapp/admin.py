from django.contrib import admin
from .models import *

admin.site.register(Principal)
admin.site.register(Teacher)
admin.site.register(Student)
admin.site.register(CustomUser)
admin.site.register(Attendance)
admin.site.register(TeacherSubjectAssignment)
admin.site.register(Subject)
admin.site.register(Exam)


