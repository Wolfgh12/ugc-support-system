import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ugc_project.settings') # Change 'ugc_project' to your actual project folder name if different
django.setup()

from django.contrib.auth.models import User
from tickets.models import StaffProfile

staff_data = [
    {'user': 'ict_admin',     'pass': 'it@ugc',  'dept': 'I.T.',       'email': 'ict.support@ugc.edu.gh'},
    {'user': 'finance_dept',  'pass': 'fin@ugc', 'dept': 'Finance',    'email': 'finance@ugc.edu.gh'},
    {'user': 'hr_officer',    'pass': 'hr@ugc',  'dept': 'HR',         'email': 'hr.desk@ugc.edu.gh'},
    {'user': 'admission_team','pass': 'adm@ugc', 'dept': 'Admission',  'email': 'admissions@ugc.edu.gh'},  
]

for person in staff_data:
    user, created = User.objects.get_or_create(username=person['user'])
    
    if created:
        user.set_password(person['pass'])
        user.email = person['email']
        user.save()
        print(f"User created: {person['user']}")
    
    # Check if they need a profile
    if not hasattr(user, 'staffprofile'):
        StaffProfile.objects.create(
            user=user,
            department=person['dept'],
            role=f"{person['dept']} Dept",
            staff_email=person['email']
        )
        print(f"Profile created for: {person['user']}")
    else:
        print(f"Staff member {person['user']} is already fully set up.")

print("--- Done! ---")