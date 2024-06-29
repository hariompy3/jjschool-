# File: myapp/management/commands/generate_dummy_data.py

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from jjapp.models import (
    Grade, Subject, Classroom, Student, Teacher, Principal,
    Notification, Attendance, Event, Exam, Result, Homework,
    Parent, TeacherSubjectAssignment, Complaint
)
from django.contrib.auth.hashers import make_password
from django.db.utils import IntegrityError
from jjapp.models import *
from django.utils import timezone
from datetime import timedelta
import random
from faker import Faker

fake = Faker()

class Command(BaseCommand):
    help = 'Generates dummy data for the school management system'

    def handle(self, *args, **kwargs):
        self.create_grades()
        print("1")
        self.create_subjects()
        print("2")
        self.create_classrooms()
        print ("3")
        self.create_users_and_roles()
        print('4')
        self.create_students()
        print('5')
        self.create_teacher_subject_assignments()
        print('6')
        self.create_notifications()
        print("7")
        #self.create_attendances()
        self.create_events()
        print('8')
        #self.create_exams_and_results()
        print('9')
  #      self.create_homeworks()
#        print("10")
        self.create_complaints()

        self.stdout.write(self.style.SUCCESS('Successfully generated dummy data'))

    def create_grades(self):
        for i in range(1, 11):
            Grade.objects.create(name=f"Grade {i}", level=i, description=f"Description for Grade {i}")

    def create_subjects(self):
        subjects = ['Math', 'Science', 'English', 'History', 'Geography', 'Art', 'Music', 'Physical Education']
        for grade in Grade.objects.all():
            for subject in subjects:
                Subject.objects.create(name=subject, grade=grade)

    def create_classrooms(self):
        for grade in Grade.objects.all():
            Classroom.objects.create(
                name=f"{grade.name} A",
                grade=grade,
                capacity=random.randint(20, 35),
                total_students=0
            )
            
            
            
            
            

    def create_users_and_roles(self):
        User = get_user_model()
        print("googogoog")

        # Create principal
#        principal_user = User.objects.create_user(
#            username='principal',
#            email='principal@school.com',
#            password='principalpass',
#            role='principal'
#        )
#        Principal.objects.create(user=principal_user, phone_number=fake.phone_number())

        # Create teachers
        for i in range(10):
          try:
              teacher_user = CustomUser.objects.create(
                username=f'teacher{i+1}',
                email=f'teacher{i+1}@school.com',
                password=make_password('teacherpass'),
                role='teacher'
            )
          except IntegrityError:
            print("Username already exists or other integrity error occurred.")
            
          

          
            Teacher.objects.create(
                user=teacher_user,
                address=fake.address(),
                phone_number=fake.phone_number(),
                date_of_birth=fake.date_of_birth(minimum_age=25, maximum_age=65),
                main_subject=random.choice(['Math', 'Science', 'English', 'History', 'Geography']),
                extra_subjects=', '.join(random.sample(['Art', 'Music', 'Physical Education'], 2))
            )

# File: myapp/management/commands/generate_dummy_data.py

# ... (previous imports and code remain the same)

    def create_students(self):
        User = get_user_model()
        grades = list(Grade.objects.all())
        classrooms = list(Classroom.objects.all())

        for i in range(100):
            grade = random.choice(grades)
            classroom = next((c for c in classrooms if c.grade == grade), None)

            first_name = fake.first_name()
            last_name = fake.last_name()
            
            student = Student.objects.create(
                id = i,
                first_name=first_name,
                last_name=last_name,
                date_of_birth=fake.date_of_birth(minimum_age=5, maximum_age=18),
                adhar_num=fake.unique.random_number(digits=12),
                admission_date=fake.date_this_decade(),
                grade=grade,
                roll_number=random.uniform(10, 100),
                classroom=classroom,
                performance=fake.text(max_nb_chars=200),
                attendance_records=fake.text(max_nb_chars=200),
                disciplinary_actions=fake.text(max_nb_chars=200),
                total_fee=random.uniform(10000, 50000),
                remaining_fee=random.uniform(0, 10000),
                attendance_percentage=random.uniform(70, 100)
            )

            # Set the password using set_password method
            student.save()

            if classroom:
                classroom.total_students += 1
                classroom.save()

#    # ... (rest of the methods remain the same)

    def create_teacher_subject_assignments(self):
        teachers = list(Teacher.objects.all())
        subjects = list(Subject.objects.all())
        grades = list(Grade.objects.all())

        for teacher in teachers:
            for _ in range(random.randint(1, 3)):
                TeacherSubjectAssignment.objects.create(
                    teacher=teacher,
                    subject=random.choice(subjects),
                    grade=random.choice(grades)
                )

    def create_notifications(self):
        for _ in range(20):
            Notification.objects.create(
                title=fake.sentence(),
                content=fake.paragraph()
            )

#    def create_attendances(self):
#        students = list(Student.objects.all())
#        teachers = list(Teacher.objects.all())
#        for _ in range(500):
#            student = random.choice(students)
#            Attendance.objects.create(
#                student=student,
#                class_teacher=random.choice(teachers),
#                date=fake.date_this_month(),
#                status=random.choice([0, 1])
#            )

    def create_events(self):
        users = list(get_user_model().objects.all())
        for _ in range(10):
            Event.objects.create(
                title=fake.sentence(),
                description=fake.paragraph(),
                date=fake.date_this_year(),
                time=fake.time(),
                venue=fake.address(),
                organizer=random.choice(users),
                event_type=random.choice(['Academic', 'Cultural', 'Sports'])
            )

    #def create_exams_and_results(self):
#        subjects = list(Subject.objects.all())
#        students = list(Student.objects.all())

#        for _ in range(5):
#            exam = Exam.objects.create(
#                name=f"{fake.word().capitalize()} Exam",
#                subject=random.choice(subjects),
#                date=fake.date_this_year(),
#                duration=timedelta(hours=random.randint(1, 3))
#            )

#            for student in random.sample(students, min(len(students), 50)):
#                Result.objects.create(
#                    student=student,
#                    exam=exam,
#                    marks=random.uniform(0, 100),
#                    grade=random.choice(['A', 'B', 'C', 'D', 'F']),
#                    subject=exam.subject,
#                    comments=fake.sentence()
#                )

    def create_homeworks(self):
        subjects = list(Subject.objects.all())
        teachers = list(Teacher.objects.all())
        grades = list(Grade.objects.all())

        for _ in range(20):
            Homework.objects.create(
                title=fake.sentence(),
                description=fake.paragraph(),
                assigned_date=fake.date_this_month(),
                due_date=fake.date_between(start_date='today', end_date='+30d'),
                subject=random.choice(subjects),
                assigned_by=random.choice(teachers),
                grade=random.choice(grades)
            )

    def create_complaints(self):
        users = list(get_user_model().objects.all())
        for _ in range(15):
            complainant = random.choice(users)
            Complaint.objects.create(
                topic=random.choice(['academic', 'behavior', 'facility', 'other']),
                description=fake.paragraph(),
                complainant=complainant,
                is_resolved=random.choice([True, False]),
                resolution_date=fake.date_this_year() if random.choice([True, False]) else None,
                complainant_role=complainant.role
            )