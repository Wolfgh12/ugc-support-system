import json
import threading
import re
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db.models import OuterRef, Subquery

# Import your models
from .models import Ticket, StaffProfile, StudentMaster, StaffMaster, TicketMessage

# --- HELPER FUNCTION FOR FAST EMAILS ---
def send_email_async(subject, email_body, recipient_list, fail_silently=False):
    """Sends emails in a background thread without slowing down the user."""
    if isinstance(recipient_list, str):
        recipient_list = [recipient_list]
        
    thread = threading.Thread(
        target=send_mail,
        args=(subject, email_body, settings.DEFAULT_FROM_EMAIL, recipient_list),
        kwargs={'fail_silently': fail_silently}
    )
    thread.start()

# --- PUBLIC VIEWS ---

def home(request):
    return render(request, 'index.html')

def public_enquiry(request):
    return render(request, 'public_enquiry.html', {
        'public_depts': Ticket.DEPARTMENT_CHOICES
    })

def track_status(request):
    return render(request, 'track_enquiry.html')

def track_query(request):
    ref_number = request.GET.get('ref', '').strip()
    match = re.search(r'\d+', ref_number)
    
    if not match:
        return JsonResponse({'error': 'Invalid format. Enter a reference like UGC-123.'}, status=400)
    
    try:
        ticket_id = int(match.group())
        ticket = Ticket.objects.get(id=ticket_id)
        
        messages_query = ticket.messages.all().order_by('created_at')
        thread = []
        for msg in messages_query:
            thread.append({
                'id': msg.id,
                'sender': msg.sender_name,
                'message': msg.message,
                'is_staff': msg.is_staff,
                'parent_id': msg.parent.id if msg.parent else None,
                'timestamp': msg.created_at.strftime("%b %d, %Y %H:%M")
            })

        data = {
            'id': ticket.id,
            'ref_id': ticket.formatted_id,
            'subject': ticket.subject,
            'department': ticket.department,
            'original_message': ticket.message,
            'status': ticket.status,
            'thread': thread,
            'reply_date': ticket.updated_at.strftime("%b %d, %Y") if ticket.updated_at else ""
        }
        return JsonResponse(data)

    except Ticket.DoesNotExist:
        return JsonResponse({'error': f'Reference UGC-{match.group()} not found.'}, status=404)
    except Exception as e:
        return JsonResponse({'error': 'An internal error occurred.'}, status=500)

def submit_ticket(request):
    if request.method == 'POST':
        try:
            if request.content_type == 'application/json':
                data = json.loads(request.body)
            else:
                data = request.POST

            name = data.get('name', '').strip()
            email = data.get('email', '').strip()
            phone = data.get('phone', '')
            raw_user_type = data.get('user_type', 'visitor').lower()
            student_id = data.get('student_id', '').strip()
            staff_id = data.get('staff_id', '').strip()
            dept = data.get('department')
            subj = data.get('subject')
            msg = data.get('message')

            if not all([name, email, dept, subj, msg]):
                return JsonResponse({'status': 'error', 'message': 'Missing fields'}, status=400)

            validated_student_obj = None
            validated_staff_obj = None
            final_user_type = 'VISITOR'

            if raw_user_type == 'student':
                try:
                    student = StudentMaster.objects.get(index_number__iexact=student_id, is_active=True)
                    validated_student_obj = student
                    final_user_type = 'STUDENT'
                except StudentMaster.DoesNotExist:
                    return JsonResponse({'status': 'error', 'message': 'Invalid Student ID'}, status=400)

            elif raw_user_type == 'staff':
                try:
                    staff = StaffMaster.objects.get(staff_id__iexact=staff_id, is_active=True)
                    validated_staff_obj = staff
                    final_user_type = 'STAFF'
                except StaffMaster.DoesNotExist:
                    return JsonResponse({'status': 'error', 'message': 'Invalid Staff ID'}, status=400)

            ticket = Ticket.objects.create(
                name=name, email=email, phone=phone,
                user_type=final_user_type,
                student_id=student_id if final_user_type == 'STUDENT' else None,
                staff_id=staff_id if final_user_type == 'STAFF' else None,
                validated_student=validated_student_obj,
                validated_staff=validated_staff_obj,
                department=dept, subject=subj, message=msg, status='Open'
            )

            user_subject = f"UGC Ticket Logged: {ticket.formatted_id}"
            user_body = f"Dear {ticket.name},\n\nYour enquiry has been received.\nReference: {ticket.formatted_id}"
            send_email_async(user_subject, user_body, [ticket.email])

            return JsonResponse({'status': 'success', 'name': ticket.name, 'ref_id': ticket.formatted_id})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error', 'message': 'POST only'}, status=405)

# --- STAFF & DASHBOARD VIEWS ---

@csrf_exempt
def get_messages(request, ticket_id):
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'Unauthorized'}, status=403)
    
    ticket = get_object_or_404(Ticket, id=ticket_id)
    messages_query = ticket.messages.all().order_by('created_at')
    
    msg_list = []
    for m in messages_query:
        msg_list.append({
            'id': m.id,
            'sender_name': m.sender_name,
            'message': m.message,
            'is_staff': m.is_staff,
            'parent_id': m.parent.id if m.parent else None,
            'created_at': m.created_at.strftime("%b %d, %H:%M")
        })
    return JsonResponse({'messages': msg_list})

@csrf_exempt
def update_status(request, ticket_id):
    if request.method == 'POST' and request.user.is_authenticated:
        try:
            data = json.loads(request.body)
            ticket = get_object_or_404(Ticket, id=ticket_id)
            ticket.status = data.get('status')
            ticket.save()
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error'}, status=400)

@csrf_exempt
def submit_reply(request, ticket_id):
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error'}, status=403)

    if request.method == 'POST':
        ticket = get_object_or_404(Ticket, id=ticket_id)
        
        if request.content_type == 'application/json':
            data = json.loads(request.body)
            reply_text = data.get('message')
            parent_id = data.get('parent_id')
        else:
            reply_text = request.POST.get('reply_message')
            parent_id = request.POST.get('parent_id')

        if not reply_text:
            return JsonResponse({'status': 'error', 'message': 'Empty reply'}, status=400)

        parent_msg = TicketMessage.objects.filter(id=parent_id).first() if parent_id else None
        actual_staff_name = request.user.get_full_name() or request.user.username
        
        try:
            user_profile = request.user.staffprofile
            dept_display = "Super Admin" if user_profile.department == 'Super Command' else f"{user_profile.department} Dept"
        except StaffProfile.DoesNotExist:
            dept_display = "Management"

        TicketMessage.objects.create(
            ticket=ticket,
            sender_name=actual_staff_name,
            message=reply_text,
            is_staff=True,
            parent=parent_msg
        )

        ticket.updated_at = timezone.now()
        ticket.save()

        subject = f"UGC Response: {ticket.formatted_id}"
        email_body = f"Hello {ticket.name},\n\nYou have a new response from {actual_staff_name} ({dept_display}).\n\n{reply_text}"
        send_email_async(subject, email_body, [ticket.email], fail_silently=True)

        return JsonResponse({'status': 'success'})

@csrf_exempt
def user_reply(request, ticket_id):
    if request.method == 'POST':
        ticket = get_object_or_404(Ticket, id=ticket_id)
        try:
            data = json.loads(request.body)
            reply_text = data.get('message', '').strip()
            parent_id = data.get('parent_id')
            
            if not reply_text:
                return JsonResponse({'status': 'error', 'message': 'Empty message'}, status=400)

            parent_msg = TicketMessage.objects.filter(id=parent_id).first() if parent_id else None

            TicketMessage.objects.create(
                ticket=ticket, 
                sender_name=ticket.name, 
                message=reply_text, 
                is_staff=False,
                parent=parent_msg
            )
            
            ticket.updated_at = timezone.now()
            ticket.save()

            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

def login_view(request):
    if request.user.is_authenticated:
        return redirect('staff_dashboard')
    if request.method == 'POST':
        user = authenticate(request, username=request.POST.get('username'), password=request.POST.get('password'))
        if user:
            auth_login(request, user)
            return redirect('staff_dashboard') 
        messages.error(request, "Invalid Credentials.")
    return render(request, 'login.html')

def logout_view(request):
    auth_logout(request)
    return redirect('home')

def staff_dashboard(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    # --- FIXED LOGIC: Renaming annotations to avoid model conflicts ---
    # 1. Subquery for the last message overall
    last_msg_subquery = TicketMessage.objects.filter(ticket=OuterRef('pk')).order_by('-created_at')
    
    # 2. Subquery for the latest staff reply
    last_staff_subquery = TicketMessage.objects.filter(ticket=OuterRef('pk'), is_staff=True).order_by('-created_at')

    # Use unique names like 'ann_message' instead of 'reply_message'
    tickets_base = Ticket.objects.annotate(
        ann_message=Subquery(last_msg_subquery.values('message')[:1]),
        ann_is_staff=Subquery(last_msg_subquery.values('is_staff')[:1]),
        ann_staff_name=Subquery(last_staff_subquery.values('sender_name')[:1])
    )

    order_by = '-updated_at'
    is_super = False

    if request.user.is_superuser:
        is_super = True
        queryset = tickets_base.all().order_by(order_by)
        display_dept = 'University-Wide (Super Command)'
        role = 'Admin'
    else:
        try:
            user_profile = request.user.staffprofile
            if user_profile.department == 'Super Command':
                is_super = True
                queryset = tickets_base.all().order_by(order_by)
                display_dept = "University-Wide (Super Command)"
            else:
                queryset = tickets_base.filter(department=user_profile.department).order_by(order_by)
                display_dept = user_profile.department
            role = user_profile.role
        except StaffProfile.DoesNotExist:
            return redirect('home')

    # Mapping annotated values to the attributes expected by dashboard.html
    for t in queryset:
        # If last message was NOT by staff, mark as USER (Triggers 'NEW' badge)
        t.last_reply_by = 'USER' if t.ann_is_staff == False else 'STAFF'
        # Assign the latest message text
        t.reply_message = t.ann_message
        # Assign the latest staff name
        t.last_staff_name = t.ann_staff_name

    return render(request, 'dashboard.html', {
        'tickets': queryset, 
        'department': display_dept, 
        'role': role,
        'is_super_command': is_super 
    })

@csrf_exempt
def delete_ticket(request, ticket_id):
    if request.user.is_authenticated:
        ticket = get_object_or_404(Ticket, id=ticket_id)
        ticket.delete()
        return JsonResponse({'status': 'deleted', 'message': 'Ticket purged.'})
    return JsonResponse({'status': 'error'}, status=403)

@csrf_exempt
def bulk_delete_tickets(request):
    if request.method == 'POST' and request.user.is_authenticated:
        try:
            data = json.loads(request.body)
            ticket_ids = data.get('ticket_ids', [])
            Ticket.objects.filter(id__in=ticket_ids).delete()
            return JsonResponse({'status': 'deleted', 'message': f'Deleted {len(ticket_ids)} tickets.'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error'}, status=405)