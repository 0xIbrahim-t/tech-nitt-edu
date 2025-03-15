from django.utils.decorators import method_decorator
from django.views.generic import View
from api.decorators.response import JsonResponseDec
from api.decorators.project_permissions import IsAdminDec, CheckAccessPrivilegeDec
from api.models import Project, User, Club, ProjectMember
from api.controllers.response_format import error_response
from api.controllers.project_utilities import create_project
from django.core.files.storage import FileSystemStorage
from django.db.models import Q
import logging
from django.forms.models import model_to_dict

logger = logging.getLogger(__name__)


def list_to_dict(items):
    '''
    Converts a given QuerySet into a list of dictionaries.
    For each item, if it has an image, replaces it with its URL.
    Also, if the item has a related club, adds the club's name.
    Additionally, includes the techstack list.
    '''
    converted = []
    for item in items:
        new_item = model_to_dict(item)
        
        # Replace the image field with its URL if it exists
        if hasattr(item, 'image'):
            new_item["image"] = item.image.url if item.image else None
        else:
            new_item["image"] = None
        
        # If the object has a 'club' attribute, add the club name
        if hasattr(item, 'club'):
            new_item["club_name"] = item.club.name if item.club else None

        # Add the techstack field
        new_item["techstack"] = item.techstack
        
        converted.append(new_item)
    return converted


@method_decorator(JsonResponseDec, name='dispatch')
class AllProjects(View):
    """
    Return all Projects
    """
    def get(self, req):
        projects = Project.objects.all()
        return {
            'data': list_to_dict(projects)
        }
    

@method_decorator(JsonResponseDec, name='dispatch')
class ProjectDetail(View):
    """
    Returns the details of a single project identified by its name.
    """
    def get(self, req, project_name):
        try:
            project = Project.objects.get(name=project_name)
        except Project.DoesNotExist:
            return error_response("Project does not exist")
        
        members_qs = project.members.all()
        members_data = []
        for member in members_qs:
            members_data.append({
                "name": member.name,
                "profile_pic": member.profile_pic.url if member.profile_pic else None
            })
        
        response_data = {
            "id": project.id,
            "name": project.name,
            "email": project.head.email,
            "abstract": project.abstract,
            "link": project.link,
            "image": project.image.url if project.image else None,
            "techstack": project.techstack,
            "members": members_data
        }
        return response_data
    


@method_decorator(JsonResponseDec, name='dispatch')
class Search(View):
    def get(self, req):
        query = req.GET.get("query")
        projects = Project.objects.filter(
            Q(head__name__unaccent__icontains=query) | 
            Q(name__unaccent__icontains=query) | 
            Q(club__name__unaccent__icontains=query)
        )
        return {
            'data': list_to_dict(projects)
        }


class Tags(View):
    def get(self, req):
        pass


@method_decorator(JsonResponseDec, name='dispatch')
@method_decorator(IsAdminDec, name='dispatch')
class Create(View):
    """
    Creates a project if user has admin access and project details (link and name) are unique.
    Now also handles the techstack images.
    """
    def post(self, req):
        name = req.POST.get("name")
        head = req.POST.get("email")
        abstract = req.POST.get("abstract")
        link = req.POST.get("link")
        club = req.POST.get("club")
        myfile = req.FILES['image']
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        uploaded_file_url = fs.url(filename)
        print(uploaded_file_url)
        
        if not req.is_admin:
            return error_response("PERMISSION DENIED TO CREATE PROJECTS")
        try:
            user = User.objects.get(email=head)
        except User.DoesNotExist:
            return error_response("User does not exist")
        
        try:
            club = Club.objects.get(name=club)
        except Club.DoesNotExist:
            return error_response("Club does not exist")

        if Project.objects.filter(name=name).exists():
            return error_response("A project with the same name exists! Please switch to a new project name")
        
        import json
        members = []
        members_json = req.POST.get("members")
        if members_json:
            try:
                members = json.loads(members_json)
                # Each member is expected to have a "name" and a "profile_pic" key.
                # If the "profile_pic" value is a key for a file in the request, attach the file.
                for member in members:
                    profile_pic_key = member.get('profile_pic')
                    if profile_pic_key and profile_pic_key in req.FILES:
                        member['profile_pic'] = req.FILES[profile_pic_key]
                    else:
                        member['profile_pic'] = None
            except Exception as e:
                return error_response("Invalid members data format: " + str(e))
        
        # Handle techstack images (multiple file upload)
        techstack_list = []
        if "techstack" in req.FILES:
            techstack_files = req.FILES.getlist("techstack")
            for tech_file in techstack_files:
                tech_filename = fs.save(tech_file.name, tech_file)
                uploaded_tech_url = fs.url(tech_filename)
                techstack_list.append(uploaded_tech_url)
        
        try:
            # Pass techstack_list to the create_project helper (make sure its signature accepts it)
            if create_project(name, abstract, link, user, uploaded_file_url, club, members=members, techstack=techstack_list):
                logger.info('Project(name={}) creation successful'.format(name))
                return "Project created successfully!"
            else:
                return error_response("Invalid details")
        except Exception as e:
            logger.error(e)
            return error_response("Project creation failed")


@method_decorator(JsonResponseDec, name='dispatch')
@method_decorator(CheckAccessPrivilegeDec, name='dispatch')
class Edit(View):
    """
    Updates following details in a project if user has "Admin" access:
    1. Abstract
    2. Link
    Also supports updating the techstack images.
    """
    def post(self, req):
        name = req.POST.get("name")
        link = req.POST.get("link")
        abstract = req.POST.get("abstract")
        if not (req.access_privilege == "Edit" or req.access_privilege == "Admin"):
            return error_response("USER DOESN'T HAVE EDIT ACCESS")
        try:
            project = Project.objects.get(name=name)
            project.link = link
            project.abstract = abstract

            # Update techstack if provided
            fs = FileSystemStorage()
            techstack_list = []
            if "techstack" in req.FILES:
                techstack_files = req.FILES.getlist("techstack")
                for tech_file in techstack_files:
                    tech_filename = fs.save(tech_file.name, tech_file)
                    uploaded_tech_url = fs.url(tech_filename)
                    techstack_list.append(uploaded_tech_url)
                project.techstack = techstack_list

            project.save()

            import json
            members_json = req.POST.get("members")
            if members_json:
                try:
                    members = json.loads(members_json)
                    # Option: Remove existing members and add the new list
                    project.members.all().delete()
                    for member_data in members:
                        profile_pic_key = member_data.get("profile_pic")
                        if profile_pic_key and profile_pic_key in req.FILES:
                            profile_pic = req.FILES[profile_pic_key]
                        else:
                            profile_pic = None
                        ProjectMember.objects.create(
                            project=project,
                            name=member_data.get("name"),
                            profile_pic=profile_pic
                        )
                except Exception as e:
                    return error_response("Invalid members data format: " + str(e))
            logger.info('Project(name={}) update successful'.format(project.name))
            return "Project updated successfully!"
        except Project.DoesNotExist:
            return error_response("Project doesn't exist")
