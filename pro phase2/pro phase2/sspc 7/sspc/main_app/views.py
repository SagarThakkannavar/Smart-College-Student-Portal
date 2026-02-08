import json
import requests
from django.contrib.auth import authenticate, login, logout

from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.views.decorators.csrf import csrf_exempt

from .EmailBackend import EmailBackend
from .models import Attendance, Session, Subject 
from .models import Course

import csv
from django.http import HttpResponse
from .models import Student

from django.shortcuts import get_object_or_404
from .models import AttendanceReport, Staff, Subject

from .models import CustomUser, Staff

from .models import StudentResult

import csv
from django.http import HttpResponse
from .models import StudentResult

def export_results_csv(request):
    # Create file response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="student_results.csv"'

    writer = csv.writer(response)
    
    # CSV Header
    writer.writerow([
        "Student Name",
        "Email",
        "Course",
        "Batch",
        "Subject",
        "IA-1",
        "IA-2",
    ])

    results = StudentResult.objects.select_related(
        "student__admin",
        "student__course",
        "student__session",
        "subject"
    )

    for result in results:
        student = result.student
        admin = student.admin

        writer.writerow([
            f"{admin.first_name} {admin.last_name}",
            admin.email,
            student.course.name if student.course else "",
            f"{student.session.start_year} - {student.session.end_year}" if student.session else "",
            result.subject.name,
            result.test,
            result.exam
        ])

    return response

#CSV for staff manage
def export_staff_csv(request):
    # Create the HttpResponse object with CSV header
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="staff_list.csv"'

    writer = csv.writer(response)
    # Write header row
    writer.writerow(['Full Name', 'Email', 'Gender', 'Course'])

    # Get all staff
    all_staff = CustomUser.objects.filter(user_type=2)  # user_type 2 = Staff
    for staff in all_staff:
        full_name = f"{staff.first_name} {staff.last_name}"
        email = staff.email
        gender = staff.gender
        course = staff.staff.course.name if hasattr(staff, 'staff') and staff.staff.course else ''
        writer.writerow([full_name, email, gender, course])

    return response
#create a addence csv
def export_attendance_csv_filtered(request):
    subject_id = request.GET.get('subject')
    session_id = request.GET.get('session')
    date_id = request.GET.get('date')

    # Filter the attendance records
    try:
        attendance = Attendance.objects.get(id=date_id, subject_id=subject_id, session_id=session_id)
    except Attendance.DoesNotExist:
        return HttpResponse("No attendance found for this selection")

    reports = AttendanceReport.objects.filter(attendance=attendance).select_related('student__admin')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="attendance_{attendance.id}.csv"'

    writer = csv.writer(response)
    writer.writerow(['Student Name', 'Status'])

    for report in reports:
        student_name = f"{report.student.admin.first_name} {report.student.admin.last_name}"
        status = "Present" if report.status else "Absent"
        writer.writerow([student_name, status])

    return response

#export CSV for admin student manage
def export_students_csv(request):
    # Create HTTP response for CSV
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="students.csv"'

    writer = csv.writer(response)
    writer.writerow(['ID', 'Full Name', 'Email', 'Course', 'Session'])

    # Fetch all students
    students = Student.objects.select_related('admin', 'course', 'session').all()

    for student in students:
        full_name = f"{student.admin.first_name} {student.admin.last_name}"
        email = student.admin.email
        course_name = student.course.name if student.course else "N/A"
        session_period = (
            f"{student.session.start_year} - {student.session.end_year}"
            if student.session else "N/A"
        )

        writer.writerow([student.id, full_name, email, course_name, session_period])

    return response



# Create your views here.


def login_page(request):
    if request.user.is_authenticated:
        if request.user.user_type == '1':
            return redirect(reverse("admin_home"))
        elif request.user.user_type == '2':
            return redirect(reverse("staff_home"))
        else:
            return redirect(reverse("student_home"))
    return render(request, 'main_app/login.html')


def doLogin(request, **kwargs):
    if request.method != 'POST':
        return HttpResponse("<h4>Denied</h4>")
    else:
        #Google recaptcha
        captcha_token = request.POST.get('g-recaptcha-response')
        captcha_url = "https://www.google.com/recaptcha/api/siteverify"
        captcha_key = "6LfTGD4qAAAAALtlli02bIM2MGi_V0cUYrmzGEGd"
        data = {
            'secret': captcha_key,
            'response': captcha_token
        }
        # Make request
        try:
            captcha_server = requests.post(url=captcha_url, data=data)
            response = json.loads(captcha_server.text)
            if response['success'] == False:
                messages.error(request, 'Invalid Captcha. Try Again')
                return redirect('/')
        except:
            messages.error(request, 'Captcha could not be verified. Try Again')
            return redirect('/')
        
        #Authenticate
        user = EmailBackend.authenticate(request, username=request.POST.get('email'), password=request.POST.get('password'))
        if user != None:
            login(request, user)
            if user.user_type == '1':
                return redirect(reverse("admin_home"))
            elif user.user_type == '2':
                return redirect(reverse("staff_home"))
            else:
                return redirect(reverse("student_home"))
        else:
            messages.error(request, "Invalid details")
            return redirect("/")



def logout_user(request):
    if request.user != None:
        logout(request)
    return redirect("/")


@csrf_exempt
def get_attendance(request):
    subject_id = request.POST.get('subject')
    session_id = request.POST.get('session')
    try:
        subject = get_object_or_404(Subject, id=subject_id)
        session = get_object_or_404(Session, id=session_id)
        attendance = Attendance.objects.filter(subject=subject, session=session)
        attendance_list = []
        for attd in attendance:
            data = {
                    "id": attd.id,
                    "attendance_date": str(attd.date),
                    "session": attd.session.id
                    }
            attendance_list.append(data)
        return JsonResponse(json.dumps(attendance_list), safe=False)
    except Exception as e:
        return None


def showFirebaseJS(request):
    data = """
    // Give the service worker access to Firebase Messaging.
// Note that you can only use Firebase Messaging here, other Firebase libraries
// are not available in the service worker.
importScripts('https://www.gstatic.com/firebasejs/7.22.1/firebase-app.js');
importScripts('https://www.gstatic.com/firebasejs/7.22.1/firebase-messaging.js');

// Initialize the Firebase app in the service worker by passing in
// your app's Firebase config object.
// https://firebase.google.com/docs/web/setup#config-object
firebase.initializeApp({
    apiKey: "AIzaSyBarDWWHTfTMSrtc5Lj3Cdw5dEvjAkFwtM",
    authDomain: "sms-with-django.firebaseapp.com",
    databaseURL: "https://sms-with-django.firebaseio.com",
    projectId: "sms-with-django",
    storageBucket: "sms-with-django.appspot.com",
    messagingSenderId: "945324593139",
    appId: "1:945324593139:web:03fa99a8854bbd38420c86",
    measurementId: "G-2F2RXTL9GT"
});

// Retrieve an instance of Firebase Messaging so that it can handle background
// messages.
const messaging = firebase.messaging();
messaging.setBackgroundMessageHandler(function (payload) {
    const notification = JSON.parse(payload);
    const notificationOption = {
        body: notification.body,
        icon: notification.icon
    }
    return self.registration.showNotification(payload.notification.title, notificationOption);
});
    """
    return HttpResponse(data, content_type='application/javascript')

