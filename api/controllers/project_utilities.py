from api.models import Project, ProjectMemberPrivilege, ProjectMemberRelationship, ProjectMember
import logging

logger = logging.getLogger(__name__)

def create_project(name, abstract, link, head, uploaded_file_url, club, members=None, techstack=None):
    """
    Helper to create a project, assign project user relationships, and store techstack images.
    """
    try:
        project_member_privilege = ProjectMemberPrivilege.objects.filter(name="Admin")
        if project_member_privilege.exists():
            project = Project.objects.create(
                name=name,
                abstract=abstract,
                link=link,
                head=head,
                image=uploaded_file_url,
                club=club,
                techstack=techstack or []
            )
            ProjectMemberRelationship.objects.create(
                project=project,
                user=head,
                privilege=project_member_privilege[0]
            )
            if members:
                for member_data in members:
                    ProjectMember.objects.create(
                        project=project,
                        name=member_data.get('name'),
                        profile_pic=member_data.get('profile_pic')
                    )
            return True
        else:
            logger.error("Admin access not found")
            return False
    except Exception as e:
        logger.error(e)
        return False
