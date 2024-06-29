from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from jjapp.models import Teacher, Subject, Grade, TeacherSubjectAssignment

User = get_user_model()

class AssignSubjectsViewTest(TestCase):
    def setUp(self):
        self.client = Client()

        # Create a principal user
        self.principal_user = User.objects.create_user(
            username='principal',
            password='password',
            role='principal'
        )
        
        # Log in as the principal user
        self.client.login(username='principal', password='password')
        
        # Create a teacher
        self.teacher_user = User.objects.create_user(
            username='teacher1',
            password='password',
            role='teacher'
        )
        self.teacher = Teacher.objects.create(
            user=self.teacher_user,
            address='123 Main St',
            phone_number='1234567890',
            date_of_birth='1980-01-01'
        )

        # Create a grade
        self.grade = Grade.objects.create(name='Grade 1', level=1)

        # Create a subject
        self.subject = Subject.objects.create(name='Math', grade=self.grade)

    def test_assign_subjects_view_loads_correctly(self):
        url = reverse('assign_subjects')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'assign_subjects.html')  # Ensure correct template is used

    def test_assign_subjects_view_post(self):
        url = reverse('assign_subjects')
        data = {
            'teacher': self.teacher.id,
            'subject': self.subject.id,
            'grade': self.grade.id
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)  # Redirects after success
        self.assertTrue(
            TeacherSubjectAssignment.objects.filter(
                teacher=self.teacher,
                subject=self.subject,
                grade=self.grade
            ).exists()
        )

    def test_assign_subjects_duplicate_entry(self):
        # First assignment
        TeacherSubjectAssignment.objects.create(
            teacher=self.teacher,
            subject=self.subject,
            grade=self.grade
        )
        
        # Try assigning the same subject again
        url = reverse('assign_subjects')
        data = {
            'teacher': self.teacher.id,
            'subject': self.subject.id,
            'grade': self.grade.id
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 400)  # Expecting bad request or specific error handling

    def test_assign_subjects_without_authentication(self):
        self.client.logout()
        url = reverse('assign_subjects')
        response = self.client.get(url)
        self.assertNotEqual(response.status_code, 200)  # Should redirect to login