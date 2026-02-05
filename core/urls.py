from django.contrib import admin
from django.urls import path
# We import the functions directly here
from tickets.views import (
    submit_ticket, 
    home, 
    public_enquiry, 
    login_view, 
    logout_view, 
    track_status,
    track_query,
    staff_dashboard,
    submit_reply,
    user_reply,
    update_status,
    delete_ticket,
    bulk_delete_tickets,
    get_messages
)

# --- UGC ADMIN BRANDING ---
admin.site.site_header = "UGC Admin Portal"
admin.site.site_title = "UGC Admin"
admin.site.index_title = "Welcome to UGC Support Command"

urlpatterns = [
    # Admin Interface
    path('admin/', admin.site.urls),
    
    # Main Pages
    path('', home, name='home'),
    path('public-enquiry/', public_enquiry, name='public_enquiry'),
    path('track-enquiry/', track_status, name='track_enquiry'),
    
    # Authentication
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    
    # Staff Area
    path('dashboard/', staff_dashboard, name='staff_dashboard'),
    
    # Status Updates
    path('update-status/<int:ticket_id>/', update_status, name='update_status'),
    
    # Delete Actions
    path('delete-ticket/<int:ticket_id>/', delete_ticket, name='delete_ticket'),
    path('bulk-delete-tickets/', bulk_delete_tickets, name='bulk_delete_tickets'),
    
    # --- REPLY & CONVERSATION ENDPOINTS ---
    path('get-messages/<int:ticket_id>/', get_messages, name='get_messages'), 
    path('submit-reply/<int:ticket_id>/', submit_reply, name='submit_reply'), 
    
    # This endpoint receives the parent_id from the tracking page
    path('user-reply/<int:ticket_id>/', user_reply, name='user_reply'),       
    
    # API Endpoints
    path('api/save-ticket/', submit_ticket, name='save_ticket'),
    path('track-query/', track_query, name='track_query'),   
]