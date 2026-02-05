from django.db import models
from django.contrib.auth.models import User 
from django.core.mail import send_mail 
from django.conf import settings 

class StudentMaster(models.Model):
    index_number = models.CharField(max_length=50, unique=True, help_text="e.g. UGC-STU-2026-001")
    full_name = models.CharField(max_length=150)
    email = models.EmailField(unique=True, null=True, blank=True) 
    course = models.CharField(max_length=100, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.index_number} - {self.full_name}"

    class Meta:
        verbose_name = "Master Student List"
        verbose_name_plural = "Master Student List"


class StaffMaster(models.Model):
    staff_id = models.CharField(max_length=50, unique=True, help_text="e.g. UGC-STF-1004")
    full_name = models.CharField(max_length=150)
    email = models.EmailField(unique=True) 
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.staff_id} - {self.full_name}"

    class Meta:
        verbose_name = "Master Staff List"
        verbose_name_plural = "Master Staff List"


# --- THE TICKET SYSTEM ---

class Ticket(models.Model):
    DEPARTMENT_CHOICES = [
        ('I.T.', 'I.T.'),
        ('Finance', 'Finance'),
        ('HR', 'HR'),
        ('Admission', 'Admission'),
        ('Student Support Service', 'Student Support Service'),
    ]

    USER_TYPE_CHOICES = [
        ('STUDENT', 'Student'),
        ('STAFF', 'Staff'),
        ('VISITOR', 'Visitor'),
    ]

    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, null=True, blank=True)
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='VISITOR')
    
    student_id = models.CharField(max_length=50, null=True, blank=True)
    staff_id = models.CharField(max_length=50, null=True, blank=True)

    validated_student = models.ForeignKey(StudentMaster, on_delete=models.SET_NULL, null=True, blank=True)
    validated_staff = models.ForeignKey(StaffMaster, on_delete=models.SET_NULL, null=True, blank=True)

    subject = models.CharField(max_length=200)
    message = models.TextField() 
    
    department = models.CharField(max_length=50, choices=DEPARTMENT_CHOICES, default='I.T.')
    status = models.CharField(max_length=20, default='Open')
    
    last_reply_by = models.CharField(max_length=20, choices=[('STAFF', 'Staff'), ('USER', 'User')], null=True, blank=True)
    
    reply_message = models.TextField(null=True, blank=True) 
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def formatted_id(self):
        if self.id is None: return "UGC-00000000"
        return f"UGC-{self.id:08d}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)

        if is_new:
            # Automatically link the first message to the thread
            TicketMessage.objects.create(
                ticket=self,
                sender_name=self.name,
                message=self.message,
                is_staff=False
            )
            
            try:
                ugc_depts = getattr(settings, 'UGC_DEPARTMENTS', {})
                central_email = getattr(settings, 'UNIVERSITY_CENTRAL_EMAIL', settings.DEFAULT_FROM_EMAIL)
                dept_email = ugc_depts.get(self.department, central_email)
                
                email_subject = f"NEW ENQUIRY ALERT: [{self.department}] - {self.formatted_id}"
                email_body = f"A new ticket has been submitted to {self.department}.\nSubject: {self.subject}"
                send_mail(email_subject, email_body, settings.DEFAULT_FROM_EMAIL, [dept_email], fail_silently=True)
            except Exception as e:
                print(f"Notification Error: {e}")

    def __str__(self):
        return f"{self.formatted_id} - {self.name}"


# --- CONVERSATION THREAD ---

class TicketMessage(models.Model):
    # Ensure related_name is 'messages' so views.py can call ticket.messages.all()
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='messages')
    
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='replies')
    
    sender_name = models.CharField(max_length=100)
    message = models.TextField()
    is_staff = models.BooleanField(default=False) 
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        # Using update() prevents the save() recursion loop while ensuring metadata updates
        Ticket.objects.filter(id=self.ticket.id).update(
            last_reply_by='STAFF' if self.is_staff else 'USER',
            reply_message=self.message,
            updated_at=models.functions.Now()
        )
        
        if not self.is_staff and self.ticket.status == 'Resolved':
            Ticket.objects.filter(id=self.ticket.id).update(status='Open')

    def __str__(self):
        return f"Msg on {self.ticket.formatted_id} by {self.sender_name}"


# --- STAFF PROFILE SECTION ---

class StaffProfile(models.Model):
    STAFF_DEPT_CHOICES = Ticket.DEPARTMENT_CHOICES + [('Super Command', 'Super Command')]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.CharField(max_length=50, choices=STAFF_DEPT_CHOICES)
    role = models.CharField(max_length=50)
    staff_email = models.EmailField()

    def __str__(self):
        return f"{self.user.username} ({self.department})"