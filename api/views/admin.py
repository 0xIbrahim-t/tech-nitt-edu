from django.contrib import admin
import logging
from django.views.generic import View
from django.utils.decorators import method_decorator
from api.decorators.response import JsonResponseDec
from api.decorators.club_permissions import IsAdminDec, CheckAccessPrivilegeDec
from api.controllers.response_format import error_response
from api.models import Club, User, ClubMemberRelationship, ClubMemberPrivilege, Project

logger = logging.getLogger(__name__)

# ------------------------------
# Overall Admin Endpoints
# ------------------------------

@method_decorator(JsonResponseDec, name='dispatch')
@method_decorator(IsAdminDec, name='dispatch')
class AdminAssignClubHead(View):
    """
    Overall admin assigns a club head to a club.
    Expects POST parameters: 
      - name: the name of the club 
      - user_email: email of the new club head
    """
    def post(self, request):
        name = request.POST.get("name")
        new_head_email = request.POST.get("user_email")
        
        if not request.is_admin:
            return error_response("Permission denied: Only overall admin can assign club heads.")
        
        try:
            club = Club.objects.get(name=name)
        except Club.DoesNotExist:
            return error_response("Club does not exist.")
        
        try:
            new_head = User.objects.get(email=new_head_email)
        except User.DoesNotExist:
            return error_response("User does not exist.")
        
        try:
            # Update the club's primary head
            club.head = new_head
            club.save()
            
            # Ensure a ClubMemberRelationship exists with "Admin" privilege
            privilege = ClubMemberPrivilege.objects.get(name="Admin")
            relationship, created = ClubMemberRelationship.objects.get_or_create(
                club=club, 
                user=new_head, 
                defaults={"privilege": privilege}
            )
            if not created:
                relationship.privilege = privilege
                relationship.save()
                
            return {"data": "Club head assigned successfully by overall admin."}
        except Exception as e:
            logger.error(e)
            return error_response("Failed to assign club head.")

@method_decorator(JsonResponseDec, name='dispatch')
@method_decorator(IsAdminDec, name='dispatch')
class AdminRemoveClubHead(View):
    """
    Overall admin removes a club head from a club.
    Expects POST parameters:
      - name: the name of the club
      - user_email: email of the club head to remove
    """
    def post(self, request):
        name = request.POST.get("name")
        head_email = request.POST.get("user_email")
        
        if not request.is_admin:
            return error_response("Permission denied: Only overall admin can remove club heads.")
        
        try:
            club = Club.objects.get(name=name)
        except Club.DoesNotExist:
            return error_response("Club does not exist.")
        
        try:
            user = User.objects.get(email=head_email)
        except User.DoesNotExist:
            return error_response("User does not exist.")
        
        try:
            relationship = ClubMemberRelationship.objects.get(club=club, user=user)
            relationship.delete()
            
            # If the removed user was the primary club head, clear the club head field.
            if club.head == user:
                club.head = None
                club.save()
                
            return {"data": "Club head removed successfully by overall admin."}
        except ClubMemberRelationship.DoesNotExist:
            return error_response("User is not a club head in this club.")
        except Exception as e:
            logger.error(e)
            return error_response("Failed to remove club head.")

# ------------------------------
# Club Head Endpoints
# ------------------------------

@method_decorator(JsonResponseDec, name='dispatch')
@method_decorator(CheckAccessPrivilegeDec, name='dispatch')
class ClubHeadAssignClubHead(View):
    """
    A club head assigns another club head within their club.
    Expects POST parameters:
      - name: the name of the club
      - user_email: email of the user to assign as club head
    Note: This endpoint uses CheckAccessPrivilegeDec to ensure that the requesting
          user has "Admin" privilege in that club.
    """
    def post(self, request):
        name = request.POST.get("name")
        new_head_email = request.POST.get("user_email")
        
        # Ensure the current user has club admin privileges for this club.
        if request.access_privilege != "Admin":
            return error_response("Permission denied: You do not have admin privileges in this club.")
        
        try:
            club = Club.objects.get(name=name)
        except Club.DoesNotExist:
            return error_response("Club does not exist.")
        
        try:
            new_head = User.objects.get(email=new_head_email)
        except User.DoesNotExist:
            return error_response("User does not exist.")
        
        try:
            privilege = ClubMemberPrivilege.objects.get(name="Admin")
            relationship, created = ClubMemberRelationship.objects.get_or_create(
                club=club, 
                user=new_head, 
                defaults={"privilege": privilege}
            )
            if not created:
                relationship.privilege = privilege
                relationship.save()
                
            return {"data": "Club head assigned successfully by club head."}
        except Exception as e:
            logger.error(e)
            return error_response("Failed to assign club head.")

@method_decorator(JsonResponseDec, name='dispatch')
@method_decorator(CheckAccessPrivilegeDec, name='dispatch')
class ClubHeadRemoveClubHead(View):
    """
    A club head removes another club head within their club.
    Expects POST parameters:
      - name: the name of the club
      - user_email: email of the club head to remove
    """
    def post(self, request):
        name = request.POST.get("name")
        head_email = request.POST.get("user_email")
        
        if request.access_privilege != "Admin":
            return error_response("Permission denied: You do not have admin privileges in this club.")
        
        try:
            club = Club.objects.get(name=name)
        except Club.DoesNotExist:
            return error_response("Club does not exist.")
        
        try:
            user = User.objects.get(email=head_email)
        except User.DoesNotExist:
            return error_response("User does not exist.")
        
        try:
            relationship = ClubMemberRelationship.objects.get(club=club, user=user)
            relationship.delete()
            
            if club.head == user:
                club.head = None
                club.save()
                
            return {"data": "Club head removed successfully by club head."}
        except ClubMemberRelationship.DoesNotExist:
            return error_response("User is not a club head in this club.")
        except Exception as e:
            logger.error(e)
            return error_response("Failed to remove club head.")
        


@method_decorator(JsonResponseDec, name='dispatch')
@method_decorator(IsAdminDec, name='dispatch')
class AdminClubsList(View):
    """
    GET: Lists all clubs.
    Route: admin/clubs
    """
    def get(self, request):
        clubs = Club.objects.all()
        clubs_data = []
        for club in clubs:
            clubs_data.append({
                "id": club.id,
                "name": club.name,
                "abstract": club.abstract,
                "link": club.link,
                "image": club.image.url if club.image else None,
                "head": club.head.email if club.head else None
            })
        return {"data": clubs_data}


@method_decorator(JsonResponseDec, name='dispatch')
@method_decorator(IsAdminDec, name='dispatch')
class AdminClubDetail(View):
    """
    GET: Returns details for a specific club.
         It includes club details, current admin users (club heads),
         and projects associated with the club.
    Route: admin/club/<name>
    """
    def get(self, request, name):
        try:
            club = Club.objects.get(name=name)
        except Club.DoesNotExist:
            return error_response("Club does not exist.")
        
        # Get all club heads (i.e. members with 'Admin' privilege) for the club.
        admin_relationships = ClubMemberRelationship.objects.filter(
            club=club, privilege__name="Admin"
        )
        admin_users = []
        for rel in admin_relationships:
            admin_users.append({
                "id": rel.user.id,
                "email": rel.user.email,
                "name": rel.user.name
            })
        
        # Get projects associated with the club.
        projects_qs = Project.objects.filter(club=club)
        projects = []
        for project in projects_qs:
            projects.append({
                "id": project.id,
                "name": project.name,
                "abstract": project.abstract,
                "link": project.link,
                "image": project.image.url if project.image else None,
                "head": project.head.email if project.head else None
            })
        
        club_data = {
            "id": club.id,
            "name": club.name,
            "abstract": club.abstract,
            "link": club.link,
            "image": club.image.url if club.image else None,
            "head": club.head.email if club.head else None,
            "admin_users": admin_users,
            "projects": projects
        }
        return {"data": club_data}

# ------------------------------
# Club Head Dashboard Endpoint
# ------------------------------

@method_decorator(JsonResponseDec, name='dispatch')
class ClubHeadDashboard(View):
    """
    GET: Club head dashboard that returns only the clubs where the
         current user (derived from the cookie/request.user) is a club head.
         For each such club, it lists:
           - Club details.
           - All current club heads (members with Admin privilege).
           - All projects associated with that club.
    Route: ${backendUrl}/club_head/
    """
    def get(self, request):
        user = request.user
        # Find clubs where the user has an admin relationship.
        relationships = ClubMemberRelationship.objects.filter(
            user=user, privilege__name="Admin"
        )
        dashboard_data = []
        for rel in relationships:
            club = rel.club
            
            # Get all club heads for this club.
            club_heads_qs = ClubMemberRelationship.objects.filter(
                club=club, privilege__name="Admin"
            )
            club_heads = []
            for ch in club_heads_qs:
                club_heads.append({
                    "id": ch.user.id,
                    "email": ch.user.email,
                    "name": ch.user.name
                })
            
            # Get projects for the club.
            projects_qs = Project.objects.filter(club=club)
            projects = []
            for project in projects_qs:
                projects.append({
                    "id": project.id,
                    "name": project.name,
                    "abstract": project.abstract,
                    "link": project.link,
                    "image": project.image.url if project.image else None,
                    "head": project.head.email if project.head else None
                })
            
            dashboard_data.append({
                "club": {
                    "id": club.id,
                    "name": club.name,
                    "abstract": club.abstract,
                    "link": club.link,
                    "image": club.image.url if club.image else None,
                    "head": club.head.email if club.head else None
                },
                "club_heads": club_heads,
                "projects": projects
            })
        return {"data": dashboard_data}
