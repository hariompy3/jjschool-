from django.shortcuts import render, redirect ,get_object_or_404
from django.contrib.auth import login, authenticate, logout
from .forms import *
from .decorators import *
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import *
from django.contrib.auth.decorators import user_passes_test


def home_page(request):
    notifications = Notification.objects.all().order_by('-created_at')
    information = "Welcome to Our School's Website! Here you'll find all the latest updates and announcements."
    return render(request, 'home.html', {'notifications': notifications, 'information': information})


def logout_view(request):
    user_role = request.user.role if request.user.is_authenticated else None
    logout(request)

    if user_role == 'student':
        return redirect('student_login')
    elif user_role == 'teacher':
        return redirect('teacher_login')
    elif user_role == 'principal':
        return redirect('principal_login')
    else:
        return redirect('home_page')
    












#principal thinks 

def principal_login(request):
    if request.method == 'POST':
        form = PrincipalForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('principal_dashboard')

    else:
        form = PrincipalForm()
    return render(request, 'principal/login.html', {'form': form})




@user_passes_test(is_principal, login_url='principal_login')
def principal_dashboard(request):
    notifications = Notification.objects.all()
    return render(request, 'principal/dashboard.html', {'notifications': notifications})




@user_passes_test(is_principal, login_url='principal_login')
def manage_notifications(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        Notification.objects.create(title=title, content=content)
        return redirect('manage_notifications')
    notifications = Notification.objects.all()
    return render(request, 'principal/manage_notifications.html', {'notifications': notifications})


@user_passes_test(is_principal, login_url='principal_login')
def edit_notification(request, notification_id):
    notification = Notification.objects.get(id=notification_id)
    if request.method == 'POST':
        notification.title = request.POST.get('title')
        notification.content = request.POST.get('content')
        notification.save()
        return redirect('manage_notifications')
    return render(request, 'principal/edit_notification.html', {'notification': notification})


@user_passes_test(is_principal, login_url='principal_login')
def delete_notification(request, notification_id):
    notification = Notification.objects.get(id=notification_id)
    notification.delete()
    return redirect('manage_notifications')

from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from .models import Student

# def is_principal(user):
#     return user.is_authenticated and user.is_principal

@user_passes_test(is_principal, login_url='principal_login')
def list_students(request):
    search_query = request.GET.get('search', '')
    students = Student.objects.filter(is_deleted=False)

    if search_query:
        students = students.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(student_id__icontains=search_query)
        )

    # Sorting
    sort_by = request.GET.get('sort', 'first_name')
    students = students.order_by(sort_by)

    # Pagination
    paginator = Paginator(students, 10)  # Show 10 students per page
    page = request.GET.get('page')
    try:
        students = paginator.page(page)
    except PageNotAnInteger:
        students = paginator.page(1)
    except EmptyPage:
        students = paginator.page(paginator.num_pages)

    context = {
        'students': students,
        'search_query': search_query,
        'sort_by': sort_by,
    }
    return render(request, 'principal/list_students.html', context)




def student_profile_for_pri(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    return render(request, 'principal/student_profile.html', {'student': student})



@user_passes_test(is_principal, login_url='principal_login')
def deleted_students(request):
        students = Student.objects.filter(is_deleted=True)
        return render(request, 'principal/deleted_students.html', {'students': students})


def soft_delete_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    student.is_deleted = True
    student.save()
    return redirect('list_students')


@user_passes_test(is_principal, login_url='principal_login')
def restore_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    student.is_deleted = False
    student.save()
    return redirect('deleted_students')


def add_student(request):
    if request.method == "POST":
        form = StudentForm(request.POST)
        if form.is_valid():
            student = form.save(commit=False)
            student.save()  
            return redirect('principal_dashboard')
    else:
        form = StudentForm()
    return render(request, 'principal/add_student.html', {'form': form})



@user_passes_test(is_principal, login_url='principal_login')
def edit_student(request, student_id):
    student_user = get_object_or_404(CustomUser, id=student_id)
    student = get_object_or_404(Student, user=student_user)
    
    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            return redirect('list_students') 
    else:
        form = StudentForm(instance=student)
    
    return render(request, 'principal/edit_student.html', {'form': form, 'student': student})


@login_required
@user_passes_test(is_principal, login_url='principal_login')
def delete_student(request, student_id):
    student_user = get_object_or_404(CustomUser, id=student_id)
    student = get_object_or_404(Student, user=student_user)
    
    if request.method == 'POST':
        student.delete()
        return redirect('list_students')
    
    return render(request, 'principal/delete_student.html', {'student': student})



@user_passes_test(is_principal, login_url='principal_login')
def add_teacher(request):
    if request.method == 'POST':
        user_form = CustomUserForm(request.POST)
        teacher_form = TeacherPriForm(request.POST)
        
        if user_form.is_valid() and teacher_form.is_valid():
            user = user_form.save(commit=False)
            user.role = 'teacher'
            user.set_password(user_form.cleaned_data['password']) 
            user.save()
            
            teacher = teacher_form.save(commit=False)
            teacher.user = user
            teacher.save()
            
            return redirect('principal_dashboard')
        else:
            error = "Please correct the errors below."
            return render(request, 'principal/add_teacher.html', {'user_form': user_form, 'teacher_form': teacher_form, 'error': error})
    else:
        user_form = CustomUserForm()
        teacher_form = TeacherPriForm()
    return render(request, 'principal/add_teacher.html', {'user_form': user_form, 'teacher_form': teacher_form})




@user_passes_test(is_principal, login_url='principal_login')
def list_teachers(request):
    teachers = Teacher.objects.all()
    return render(request, 'principal/list_teachers.html', {'teachers': teachers})


@user_passes_test(is_principal, login_url='principal_login')
def edit_teacher(request, teacher_id):
    teacher_user = get_object_or_404(CustomUser, id=teacher_id)
    teacher = get_object_or_404(Teacher, user=teacher_user)
    
    if request.method == 'POST':
        user_form = CustomUserForm(request.POST, instance=teacher_user)
        teacher_form = TeacherForm(request.POST, instance=teacher)
        if user_form.is_valid() and teacher_form.is_valid():
            user_form.save()
            teacher_form.save()
            return redirect('list_teachers')
    else:
        user_form = CustomUserForm(instance=teacher_user)
        teacher_form = TeacherForm(instance=teacher)
    
    return render(request, 'principal/edit_teacher.html', {'user_form': user_form, 'teacher_form': teacher_form})


@user_passes_test(is_principal, login_url='principal_login')
def delete_teacher(request, teacher_id):
    teacher_user = get_object_or_404(CustomUser, id=teacher_id)
    teacher = get_object_or_404(Teacher, user=teacher_user)
    
    if request.method == 'POST':
        teacher_user.delete()
        return redirect('list_teachers')
    
    return render(request, 'principal/delete_teacher.html', {'teacher': teacher})


@user_passes_test(is_principal, login_url='principal_login')
def view_student_details(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    return render(request, 'principal/view_student_details.html', {'student': student})


@user_passes_test(is_principal, login_url='principal_login')
def view_teacher_details(request, teacher_id):
    teacher = get_object_or_404(Teacher, id=teacher_id)
    return render(request, 'principal/view_teacher_details.html', {'teacher': teacher})


@user_passes_test(is_principal, login_url='principal_login')
def view_attendance_records(request):
    attendance_records = Attendance.objects.all()
    return render(request, 'principal/view_attendance_records.html', {'attendance_records': attendance_records})


@user_passes_test(is_principal, login_url='principal_login')
def view_performance_reports(request):
    students = Student.objects.all()
    return render(request, 'principal/view_performance_reports.html', {'students': students})




from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Student, Attendance, Teacher
from .forms import AttendanceForm

def is_teacher(user):
    return user.is_authenticated and user.role == 'teacher'
# views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Student, Attendance, Teacher
from django.contrib import messages

@user_passes_test(is_teacher, login_url='teacher_login')
def add_attendance(request):
    today = timezone.now().date()
    teacher = request.user.teacher
    students = Student.objects.filter(grade=teacher.class_teacher_of_grade).order_by('first_name', 'last_name')

    if request.method == 'POST':
        for student in students:
            status = request.POST.get(f'status_{student.pk}', '0')  # Default to '0' (Absent)
            attendance, created = Attendance.objects.get_or_create(
                student=student,
                date=today,
                defaults={'status': status, 'class_teacher': teacher}
            )
            if not created:
                attendance.status = status
                attendance.save()

        messages.success(request, "Attendance has been recorded successfully.")
        return redirect('teachers_dashboard')

    attendance_exists = Attendance.objects.filter(student__in=students, date=today).exists()
    class_name = teacher.class_teacher_of_grade

    context = {
        'today': today,
        'class_name': class_name,
        'students': students,
        'attendance_exists': attendance_exists,
    }

    return render(request, 'teacher/add_attendance.html', context)

from django.shortcuts import render
from .models import Student, Attendance
from datetime import date
from django.utils.dateparse import parse_date

def list_attendance(request):
    class_teacher = request.user.teacher
    students = Student.objects.filter(grade=class_teacher.class_teacher_of_grade, is_deleted=False).order_by('first_name')
    
    # Get the selected date from the request or default to today
    selected_date = request.GET.get('attendance_date')
    if selected_date:
        selected_date = parse_date(selected_date)
    else:
        selected_date = date.today()

    # Get attendance records for the selected date
    attendance_records = {attendance.student.pk: attendance.status for attendance in Attendance.objects.filter(date=selected_date)}

    context = {
        'students': students,
        'attendance_records': attendance_records,
        'selected_date': selected_date,
        'class_name': class_teacher.class_teacher_of_grade,
    }

    return render(request, 'teacher/list_attendance.html', context)













def teacher_login(request):
    if request.method == 'POST':
        form = TeacherLogForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None and user.role == 'teacher':  # Ensure the user is a teacher
                login(request, user)
                return redirect('teachers_dashboard')
            else:
                form.add_error(None, 'Invalid username or password.')
    else:
        form = TeacherLogForm()
    return render(request, 'teacher/login.html', {'form': form})


@user_passes_test(is_teacher, login_url='teacher_login')
def teachers_dashboard(request):
    return render(request, 'teacher/dashboard.html')



def student_login(request):
    if request.method == 'POST':
        form = StudentLogForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('student_dashboard')
            else:
                form.add_error(None, 'Invalid username or password.')
    else:
        form = StudentLogForm()
    return render(request, 'student/login.html', {'form': form})










from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from .models import Grade
from .forms import GradeForm


@user_passes_test(is_principal, login_url='principal_login')
def list_grades(request):
    grades = Grade.objects.all()
    return render(request, 'principal/list_grades.html', {'grades': grades})

@user_passes_test(is_principal, login_url='principal_login')
def add_grade(request):
    if request.method == 'POST':
        form = GradeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('list_grades')
    else:
        form = GradeForm()
    return render(request, 'principal/add_grade.html', {'form': form})

@user_passes_test(is_principal, login_url='principal_login')
def delete_grade(request, grade_id):
    grade = get_object_or_404(Grade, id=grade_id)
    if request.method == 'POST':
        grade.delete()
        return redirect('list_grades')
    return render(request, 'principal/delete_grade.html', {'grade': grade})



















from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.db import IntegrityError


def check_aadhaar(request):
    if request.method == 'POST':
        form = AadhaarForm(request.POST)
        if form.is_valid():
            adhar_num = form.cleaned_data['adhar_num']
            try:
                student = Student.objects.get(adhar_num=adhar_num)
                return redirect('register_student', student_id=student.id)
            except Student.DoesNotExist:
                form.add_error('adhar_num', 'Aadhaar number not found.')
    else:
        form = AadhaarForm()
    return render(request, 'student/check_aadhaar.html', {'form': form})

# jjapp/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.db import IntegrityError

from .models import Student

from django.shortcuts import render, redirect, get_object_or_404
from django.db import IntegrityError
from .models import Student
from .forms import CustomUserForm

def register_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    if request.method == 'POST':
        user_form = CustomUserForm(request.POST)
        if user_form.is_valid():
            try:
                user = user_form.save(commit=False)
                user.role = 'student'
                user.set_password(user_form.cleaned_data['password'])
                user.save()
                student.user = user
                student.save()
                return redirect('student_login')
            except IntegrityError:
                user_form.add_error(None, 'A user with this username already exists.')
    else:
        user_form = CustomUserForm()
    return render(request, 'student/register_student.html', {'user_form': user_form, 'student': student})









def principal_login(request):
    if request.method == 'POST':
        form = PrincipalForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('principal_dashboard')

    else:
        form = PrincipalForm()
    return render(request, 'principal/login.html', {'form': form})






def login_student(request):
    if request.method == 'POST':
        form = StudentLogForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('student_dashboard')
            else:
                form.add_error(None, 'Invalid username or password.')
    else:
        form = StudentLogForm()
    return render(request, 'student/login.html', {'form': form})


@user_passes_test(is_student, login_url='student_login')
def student_dashboard(request):
    return render(request, 'student/dashboard.html')





from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from .models import Complaint
from .forms import ComplaintForm, ComplaintResolutionForm

@login_required
def file_complaint(request):
    if request.method == 'POST':
        form = ComplaintForm(request.POST)
        if form.is_valid():
            complaint = form.save(commit=False)
            complaint.complainant = request.user
            complaint.complainant_role = request.user.role  # set the complainant role
            complaint.save()
            return redirect('complaint_list')
    else:
        form = ComplaintForm()
    return render(request, 'file_complaint.html', {'form': form})

@login_required
def complaint_list(request):
    complaints = Complaint.objects.all()
    return render(request, 'complaint_list.html', {'complaints': complaints})

@user_passes_test(is_principal, login_url='principal_login')
def resolve_complaint(request, complaint_id):
    complaint = Complaint.objects.get(id=complaint_id)
    if request.method == 'POST':
        form = ComplaintResolutionForm(request.POST, instance=complaint)
        if form.is_valid():
            if form.cleaned_data['is_resolved']:
                complaint.resolution_date = timezone.now()
            form.save()
            return redirect('complaint_list')
    else:
        form = ComplaintResolutionForm(instance=complaint)
    return render(request, 'resolve_complaint.html', {'form': form, 'complaint': complaint})









from django.shortcuts import render, redirect, get_object_or_404
from .models import Grade, Subject
from .forms import PrincipalSubjectForm

from django.shortcuts import render, redirect, get_object_or_404
from django.forms import ModelForm
from django.contrib.auth.decorators import user_passes_test
from .models import Classroom, Subject, Grade, Teacher, TeacherSubjectAssignment
from .forms import ClassroomForm, SubjectForm, TeacherSubjectForm

# Ensure only principals can access this view
#@user_passes_test(lambda user: user.is_authenticated and user.role == 'principal', login_url='principal_login')
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import user_passes_test
from .models import Classroom, Subject
from .forms import ClassroomForm, SubjectForm

#@user_passes_test(lambda user: user.is_authenticated and user.role == 'principal', login_url='principal_login')

# jjapp/views.py
from django.shortcuts import render, redirect, get_object_or_404
from .models import Grade, Subject
from .forms import SubjectForm

from .models import Classroom

def add_grade_subjects(request, grade_id):
    grade = get_object_or_404(Grade, pk=grade_id)

    if request.method == 'POST':
        form = SubjectForm(request.POST)
        if form.is_valid():
            subject = form.save(commit=False)
            subject.grade = grade

            # Assuming you have a classroom associated with the grade
            classroom = Classroom.objects.filter(grade=grade).first()
            if classroom:
                subject.classroom = classroom
            else:
                # Handle the case where no classroom exists for the grade
                # You can either create a new classroom or handle the error differently
                pass

            subject.save()
            return redirect('grade_detail', grade_id=grade.id)
    else:
        form = SubjectForm()

    return render(request, 'add_grade_subjects.html', {'form': form, 'grade': grade})
#@user_passes_test(lambda user: user.is_authenticated and user.role == 'teacher', login_url='teacher_login')
from django.shortcuts import render, redirect
from .forms import TeacherSubjectAssignmentForm
from .models import TeacherSubjectAssignment
from django.shortcuts import render, redirect
from .forms import TeacherSubjectAssignmentForm
from .models import TeacherSubjectAssignment
from django.shortcuts import render, redirect
from .forms import TeacherSubjectAssignmentForm
from .models import TeacherSubjectAssignment


@login_required
def teacher_subjects(request):
    try:
        teacher = request.user.teacher
    except Teacher.DoesNotExist:
        return redirect('not_authorized')
    
    subjects = TeacherSubjectAssignment.objects.filter(teacher=teacher)
    can_add_more = subjects.count() < 5
    
    return render(request, 'teacher_subjects.html', {
        'assignment': subjects,
        'can_add_more': can_add_more
    })


def add_subject(request):
    try:
        teacher = request.user.teacher
    except Teacher.DoesNotExist:
        return redirect('not_authorized')
    
    if request.method == 'POST':
        form = TeacherSubjectAssignmentForm(request.POST, teacher=teacher)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.teacher = teacher
            try:
                assignment.save()
                messages.success(request, "Subject assigned successfully.")
                return redirect('teacher_subjects')
            except IntegrityError:
                messages.error(request, "You've already assigned this subject for this grade.")
    else:
        form = TeacherSubjectAssignmentForm(teacher=teacher)
    
    return render(request, 'add_subject.html', {'form': form})

def load_subjects(request):
    grade_id = request.GET.get('grade')
    subjects = Subject.objects.filter(grade_id=grade_id).order_by('name')
    return render(request, 'subject_dropdown_list_options.html', {'subjects': subjects})

@login_required
def remove_subject(request, assignment_id):
    assignment = get_object_or_404(TeacherSubjectAssignment, id=assignment_id, teacher=request.user.teacher)
    assignment.delete()
    messages.success(request, "Subject removed successfully.")
    return redirect('teacher_subjects')

# def load_subjects(request):
#     grade_id = request.GET.get('grade')
#     subjects = Subject.objects.filter(grade_id=grade_id).order_by('name')
#     return render(request, 'subject_dropdown_list_options.html', {'subjects': subjects})

def not_authorized(request):
    return render(request, 'not_authorized.html')



from django.shortcuts import render, get_object_or_404
from .models import Grade, Subject

def grade_detail(request, grade_id):
    grade = get_object_or_404(Grade, pk=grade_id)
    subjects = Subject.objects.filter(grade=grade)
    context = {
        'grade': grade,
        'subjects': subjects,
    }
    return render(request, 'grade_detail.html', context)







# jjapp/views.py

# jjapp/views.py

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Student
from .forms import StudentProfileUpdateForm

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Student
from .forms import StudentProfileForm  # Assuming you have this form

@login_required
def student_profile(request):
    try:
        student = Student.objects.get(adhar_num=request.user.username)  # Assuming aadhaar_num is unique
    except Student.DoesNotExist:
        student = None

    if request.method == 'POST':
        form = StudentProfileForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            return redirect('student_profile')
    else:
        form = StudentProfileForm(instance=student)
    
    context = {
        'student': student,
        'form': form
    }
    return render(request, 'student/profile.html', context)






















@user_passes_test(is_teacher, login_url='teacher_login')
def exam_list(request):
    exams = Exam.objects.all()
    return render(request, 'exam_list.html', {'exams': exams})



@login_required 
@user_passes_test(is_teacher)
def teacher_classes(request, exam_id):
    teacher = request.user.teacher
    assignments = TeacherSubjectAssignment.objects.filter(teacher=teacher)
    exam = get_object_or_404(Exam, id=exam_id)
    return render(request, 'teacher_classes.html', {'assignments': assignments, 'exam': exam})






@login_required
@user_passes_test(is_teacher)
def class_students(request, exam_id, assignment_id):
    assignment = get_object_or_404(TeacherSubjectAssignment, id=assignment_id, teacher=request.user.teacher)
    exam = get_object_or_404(Exam, id=exam_id)
    students = Student.objects.filter(grade=assignment.grade)
    return render(request, 'class_students.html', {
        'assignment': assignment,
        'exam': exam,
        'students': students
    })




@login_required
@user_passes_test(is_teacher)
def add_edit_result(request, exam_id, assignment_id, student_id):
    assignment = get_object_or_404(TeacherSubjectAssignment, id=assignment_id, teacher=request.user.teacher)
    exam = get_object_or_404(Exam, id=exam_id)
    student = get_object_or_404(Student, id=student_id, grade=assignment.grade)
    assignment = assignment.subject
    result, created = Result.objects.get_or_create(
        student=student,
        exam=exam,
        subject=assignment
    )

    if request.method == 'POST':
        form = ResultForm(request.POST, instance=result)
        if form.is_valid():
            form.save()
            messages.success(request, 'Result saved successfully.')
            return redirect('class_students', exam_id=exam_id, assignment_id=assignment_id)
    else:
        form = ResultForm(instance=result)

    return render(request, 'add_edit_result.html', {
        'form': form,
        'assignment': assignment,
        'exam': exam,
        'student': student,
    })
    
    





     
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Q
from django.contrib import messages
from .models import Student
from .forms import FeePaymentForm

def is_principal(user):
    return user.is_authenticated and user.role == 'principal'

#@user_passes_test(is_principal)
def student_fee_list(request):
    query = request.GET.get('query', '')
    if query:
        students = Student.objects.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(roll_number__icontains=query)
        )
    else:
        students = Student.objects.all()

    return render(request, 'student_fee_list.html', {'students': students, 'query': query})

#vg@user_passes_test(is_principal)
def student_fee_detail(request, student_id):
    student = get_object_or_404(Student, pk=student_id)
    if request.method == 'POST':
        form = FeePaymentForm(request.POST)
        if form.is_valid():
            amount_paid = form.cleaned_data['amount_paid']
            student.update_fees(amount_paid)
            
            if amount_paid > student.remaining_fee:
                overpayment = amount_paid - student.remaining_fee
                messages.success(request, f"Fee payment of {student.remaining_fee} successfully recorded for {student.first_name} {student.last_name}. Overpayment of {overpayment} added to advanced payment.")
            else:
                messages.success(request, f"Fee payment of {amount_paid} successfully recorded for {student.first_name} {student.last_name}")
            
            return redirect('student_fee_detail', student_id=student.pk)
    else:
        form = FeePaymentForm()

    return render(request, 'student_fee_detail.html', {'student': student, 'form': form})    
    
    
   













@login_required
def student_exam_list(request):
    student = get_object_or_404(Student, adhar_num=request.user.username)
    exams = Result.objects.filter(grade=student.grade)
    return render(request, 'student/exam_list.html', {'exams': exams})

@login_required
def student_exam_results(request, exam_id):
    student = get_object_or_404(Student, user=request.user)
    exam = get_object_or_404(Exam, id=exam_id, grade=student.grade)
    results = Result.objects.filter(student=student, exam=exam)
    return render(request, 'student/exam_results.html', {'exam': exam, 'results': results})

