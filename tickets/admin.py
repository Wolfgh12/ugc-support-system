from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from .models import Ticket, StaffProfile, StudentMaster, StaffMaster, TicketMessage

# --- 1. MASTER LIST MANAGEMENT ---

@admin.register(StudentMaster)
class StudentMasterAdmin(admin.ModelAdmin):
    list_display = ('index_number', 'full_name', 'course', 'is_active', 'created_at')
    search_fields = ('index_number', 'full_name', 'email')
    list_filter = ('is_active', 'course')
    list_editable = ('is_active',)

@admin.register(StaffMaster)
class StaffMasterAdmin(admin.ModelAdmin):
    list_display = ('staff_id', 'full_name', 'email', 'is_active')
    search_fields = ('staff_id', 'full_name', 'email')
    list_filter = ('is_active',)
    list_editable = ('is_active',)

# --- 2. USER & STAFF PROFILE INTEGRATION ---

class StaffProfileInline(admin.StackedInline):
    model = StaffProfile
    can_delete = False
    verbose_name_plural = 'Staff Department Info'

class UserAdmin(BaseUserAdmin):
    inlines = (StaffProfileInline,)
    list_display = ('username', 'email', 'is_staff', 'colored_department')

    def colored_department(self, instance):
        dept = instance.staffprofile.department if hasattr(instance, 'staffprofile') else "No Dept"
        color = "#c5a059" if dept == "Super Command" else "#888"
        # FIX: Pass color and dept as arguments
        return format_html('<span style="color: {}; font-weight: bold;">{}</span>', color, dept)
    
    colored_department.short_description = 'Department'

admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# --- 3. CONVERSATION INLINE ---

class TicketMessageInline(admin.TabularInline):
    model = TicketMessage
    extra = 0
    readonly_fields = ('sender_name', 'message', 'is_staff', 'created_at')
    can_delete = False
    verbose_name = "Conversation Message"
    verbose_name_plural = "Conversation Thread"

# --- 4. UPDATED TICKET ADMIN ---

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('formatted_id', 'name', 'user_type', 'colored_status', 'colored_reply_by', 'colored_dept', 'id_verified', 'updated_at')
    list_filter = ('user_type', 'department', 'status', 'last_reply_by', 'created_at')
    search_fields = ('name', 'subject', 'email', 'student_id', 'staff_id')
    readonly_fields = ('created_at', 'updated_at')
    
    inlines = [TicketMessageInline]

    def colored_reply_by(self, obj):
        """Highlights USER replies in Gold."""
        if obj.last_reply_by == "USER":
            # FIX: Explicitly pass the label text
            return format_html(
                '<span style="background-color: #c5a059; color: white; padding: 3px 7px; border-radius: 3px; font-weight: bold;">{}</span>',
                "NEW REPLY"
            )
        label = "Staff Replied" if obj.last_reply_by == "STAFF" else "No Activity"
        return format_html('<span style="color: #888;">{}</span>', label)
    
    colored_reply_by.short_description = 'Last Action'

    def colored_status(self, obj):
        colors = {'Open': '#28a745', 'In-Progress': '#ffc107', 'Resolved': '#dc3545'}
        color = colors.get(obj.status, '#888')
        # FIX: Pass all three placeholders (color, border-color, text)
        return format_html(
            '<strong style="color: {}; border: 1px solid {}; padding: 2px 8px; border-radius: 4px;">{}</strong>',
            color, color, obj.status
        )
    colored_status.short_description = 'Status'

    def colored_dept(self, obj):
        # FIX: Pass obj.department as argument
        return format_html('<span style="color: #c5a059; font-weight: bold;">#{}</span>', obj.department)
    colored_dept.short_description = 'Dept'

    def id_verified(self, obj):
        if obj.user_type == 'VISITOR':
            return False 
        return bool(obj.validated_student or obj.validated_staff)
    
    id_verified.boolean = True
    id_verified.short_description = 'Verified'

    ordering = ('-updated_at',)

# --- 5. STANDALONE PROFILE VIEW ---

@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'department', 'role', 'staff_email')
    search_fields = ('user__username', 'department', 'staff_email')
    list_filter = ('department', 'role')

    