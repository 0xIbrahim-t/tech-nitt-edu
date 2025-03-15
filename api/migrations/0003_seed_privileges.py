# your_project/api/migrations/0002_seed_privileges.py
from django.db import migrations
from django.contrib.auth.hashers import make_password

def create_privileges(apps, schema_editor):
    print("Running seed migration...")
    # Get models using the historical version from the migration's state.
    ClubMemberPrivilege = apps.get_model('api', 'ClubMemberPrivilege')
    ProjectMemberPrivilege = apps.get_model('api', 'ProjectMemberPrivilege')
    User = apps.get_model('api', 'User')
    Club = apps.get_model('api', 'Club')
    Project = apps.get_model('api', 'Project')
    ProjectMember = apps.get_model('api', 'ProjectMember')  # New addition for project members

    # Create Club Member Privileges
    ClubMemberPrivilege.objects.get_or_create(
        name="View",
        defaults={'code': 1}
    )
    ClubMemberPrivilege.objects.get_or_create(
        name="Admin",
        defaults={'code': 2}
    )

    # Create Project Member Privileges
    ProjectMemberPrivilege.objects.get_or_create(
        name="View",
        defaults={'code': 1}
    )
    ProjectMemberPrivilege.objects.get_or_create(
        name="Admin",
        defaults={'code': 2}
    )

    # Create a dummy user for testing.
#     dummy_email = "dummy@example.com"
#     dummy_name = "Dummy User"
#     dummy_password = "password123"  # Adjust as needed.

#     dummy_user_qs = User.objects.filter(email=dummy_email)
#     if dummy_user_qs.exists():
#         dummy_user = dummy_user_qs.first()
#     else:
#         dummy_user = User.objects.create(
#             email=dummy_email,
#             name=dummy_name,
#             password=make_password(dummy_password)
#         )

#     # Create a dummy club with the dummy user as the head.
#     club, _ = Club.objects.get_or_create(
#         name="Dummy Club22",
#         defaults={
#             'abstract': "This is a dummy club for testing purposes.",
#             'link': "http://dummyclub.example.com",
#             'head': dummy_user,
#             'image': None  # Using None instead of an empty string.
#         }
#     )

#     # Create a dummy project for that club.
#     project, _ = Project.objects.get_or_create(
#         name="Dummy Project22",
#         defaults={
#             'abstract': "This is a dummy project belonging to Dummy Club.",
#             'link': "http://dummyproject.example.com",
#             'club': club,
#             'head': dummy_user,
#             'image': None  # Using None for the image.
#         }
#     )

#     # Create dummy project members for the dummy project.
#     ProjectMember.objects.get_or_create(
#         project=project,
#         name="Member One",
#         defaults={'profile_pic': None}
#     )
#     ProjectMember.objects.get_or_create(
#         project=project,
#         name="Member Two",
#         defaults={'profile_pic': None}
#     )
#     print("Seeding complete.")

# def reverse_func(apps, schema_editor):
#     # Reverse function to delete seeded data if the migration is undone.
#     ClubMemberPrivilege = apps.get_model('api', 'ClubMemberPrivilege')
#     ProjectMemberPrivilege = apps.get_model('api', 'ProjectMemberPrivilege')
#     User = apps.get_model('api', 'User')
#     Club = apps.get_model('api', 'Club')
#     Project = apps.get_model('api', 'Project')
#     ProjectMember = apps.get_model('api', 'ProjectMember')  # New addition for project members

#     ProjectMember.objects.filter(project__name="Dummy Project22").delete()
#     Project.objects.filter(name="Dummy Project22").delete()
#     Club.objects.filter(name="Dummy Club22").delete()
#     User.objects.filter(email="dummy@example.com").delete()
#     ClubMemberPrivilege.objects.filter(name__in=["View", "Admin"]).delete()
#     ProjectMemberPrivilege.objects.filter(name__in=["View", "Admin"]).delete()

class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_projectmember'),
    ]

    operations = [
        migrations.RunPython(create_privileges, reverse_func),
    ]
