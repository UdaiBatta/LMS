from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import Semester, Session
from result.models import Result, TakenCourse
from accounts.models import Student


class Command(BaseCommand):
    help = 'Manage semester and result status'

    def add_arguments(self, parser):
        parser.add_argument(
            '--action',
            type=str,
            help='Action to perform: status, close-registration, open-registration',
        )
        parser.add_argument(
            '--semester-id',
            type=int,
            help='Semester ID to work with',
        )

    def handle(self, *args, **options):
        action = options.get('action')
        semester_id = options.get('semester_id')

        if action == 'status':
            self.show_status()
        elif action == 'close-registration':
            self.close_registration(semester_id)
        elif action == 'open-registration':
            self.open_registration(semester_id)
        else:
            self.stdout.write(
                self.style.WARNING('Available actions: status, close-registration, open-registration')
            )

    def show_status(self):
        """Show current semester and registration status"""
        self.stdout.write(self.style.SUCCESS('\n=== SEMESTER STATUS ==='))
        
        current_session = Session.objects.filter(is_current_session=True).first()
        current_semester = Semester.objects.filter(is_current_semester=True).first()
        
        if current_session:
            self.stdout.write(f"Current Session: {current_session.session}")
        else:
            self.stdout.write(self.style.WARNING("No current session set"))
            
        if current_semester:
            self.stdout.write(f"Current Semester: {current_semester.semester}")
            if current_semester.session:
                self.stdout.write(f"Semester Session: {current_semester.session.session}")
            
            # Check registration status (simple logic)
            today = timezone.now().date()
            if current_semester.next_semester_begins and today >= current_semester.next_semester_begins:
                registration_status = "CLOSED (Semester has begun)"
            else:
                registration_status = "OPEN (Registration period)"
                
            self.stdout.write(f"Registration Status: {registration_status}")
        else:
            self.stdout.write(self.style.WARNING("No current semester set"))

        # Show all semesters
        self.stdout.write(self.style.SUCCESS('\n=== ALL SEMESTERS ==='))
        semesters = Semester.objects.all().order_by('id')
        for sem in semesters:
            status = "CURRENT" if sem.is_current_semester else "INACTIVE"
            session_name = sem.session.session if sem.session else "No session"
            self.stdout.write(f"ID: {sem.id}, {sem.semester} ({session_name}) - {status}")

        # Show student statistics
        self.stdout.write(self.style.SUCCESS('\n=== STUDENT STATISTICS ==='))
        total_students = Student.objects.count()
        students_with_courses = TakenCourse.objects.values('student').distinct().count()
        self.stdout.write(f"Total Students: {total_students}")
        self.stdout.write(f"Students with Registered Courses: {students_with_courses}")

    def close_registration(self, semester_id):
        """Close registration for a semester (set as current and begun)"""
        if not semester_id:
            self.stdout.write(self.style.ERROR("Please provide --semester-id"))
            return
            
        try:
            semester = Semester.objects.get(id=semester_id)
            
            # Set as current semester
            Semester.objects.filter(is_current_semester=True).update(is_current_semester=False)
            semester.is_current_semester = True
            
            # Set semester as begun (close registration)
            if not semester.next_semester_begins:
                semester.next_semester_begins = timezone.now().date()
            
            semester.save()
            
            self.stdout.write(
                self.style.SUCCESS(f'Closed registration for semester: {semester.semester}')
            )
            self.stdout.write('Students can no longer register for courses in this semester.')
            
        except Semester.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Semester with ID {semester_id} not found'))

    def open_registration(self, semester_id):
        """Open registration for a semester"""
        if not semester_id:
            self.stdout.write(self.style.ERROR("Please provide --semester-id"))
            return
            
        try:
            semester = Semester.objects.get(id=semester_id)
            
            # Set as current semester
            Semester.objects.filter(is_current_semester=True).update(is_current_semester=False)
            semester.is_current_semester = True
            
            # Clear the begin date to allow registration
            semester.next_semester_begins = None
            semester.save()
            
            self.stdout.write(
                self.style.SUCCESS(f'Opened registration for semester: {semester.semester}')
            )
            self.stdout.write('Students can now register for courses in this semester.')
            
        except Semester.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Semester with ID {semester_id} not found'))
