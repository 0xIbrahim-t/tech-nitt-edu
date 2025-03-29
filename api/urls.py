from django.urls import re_path as url
from .views import user, project, club, admin
from django.conf import settings
from django.conf.urls.static import static

# namespacing app
app_name = 'api'

urlpatterns = [

    # User-auth routes
    url('user/login/', user.LoginFormView.as_view(), name='user-login'),
    url('user/logout/', user.LogoutView.as_view(), name='user-logout'),
    url('user/register/', user.RegisterFormView.as_view(), name='user-register'),
    url('user/pass_reset/', user.ResetPassRequest.as_view(), name='user-pass-reset'),
    url('user/pass_update/', user.ResetPassUpdate.as_view(), name='user-pass-update'),
    url('user/isloggedin/', user.IsLoggedInView.as_view(), name='user-isloggedin'),
    url('user/redirect/', user.UserRedirectView.as_view(), name='user-redirect'),

    # # Admin-user routes
    # url('admin_users', admin_user.AllUsers.as_view(), name='admin-users'),
    # url('admin_user/project/', admin_user.Profile.as_view(), name='project-profile'),
    # url('admin_user/update_roles/', admin_user.AssignRoles.as_view(), name='update-roles'),
    # url('admin_user/create_tags/', admin_user.CreateTags.as_view(), name='create-tags'),
    # url('admin_user/add_members/', admin_user.AddMembers.as_view(), name='add-members'),

    # Project routes
    #search route: pass a parameter type (name, club, tag) and value
    url('projects', project.AllProjects.as_view(), name='projects-all'),
    url('project/search', project.Search.as_view(), name='project-search'),
    # create route 
    url('project/create', project.Create.as_view(), name='project-create'),
    url(r'^project/(?P<project_name>[\w\s-]+)$', project.ProjectDetail.as_view(), name='project-detail'),
    # edit route 
    url('project/edit', project.Edit.as_view(), name='project-edit'),
    #Tags
    # url('project/tags', project.Tags.as_view(), name='tags'),

	# Club routes
    #search route: pass a parameter type (name) and value
    url('clubs', club.AllClubs.as_view(), name='club-all'),
    url('club/search', club.Search.as_view(), name='club-search'),
    # create route 
    url('club/create', club.Create.as_view(), name='club-create'),
    url(r'^club/(?P<club_name>[\w\s-]+)$', club.ClubDetail.as_view(), name='club-detail'),
    # edit route 
    url('club/edit', club.Edit.as_view(), name='club-edit'),

    #Tags
    # url('club/tags', club.Tags.as_view(), name='tags'),

    # Overall Admin Endpoints
    url('admin/club/assign_head/', admin.AdminAssignClubHead.as_view(), name='admin-assign-club-head'),
    url('admin/club/remove_head/', admin.AdminRemoveClubHead.as_view(), name='admin-remove-club-head'),
    url('admin/clubs', admin.AdminClubsList.as_view(), name='admin-clubs-list'),
    url(r'^admin/club/(?P<name>[\w\s-]+)$', admin.AdminClubDetail.as_view(), name='admin-club-detail'),

    # Club Head Endpoints
    url('club_head/assign_head/', admin.ClubHeadAssignClubHead.as_view(), name='club_head-assign-club-head'),
    url('club_head/remove_head/', admin.ClubHeadRemoveClubHead.as_view(), name='club_head-remove-club-head'),
    url('club_head/', admin.ClubHeadDashboard.as_view(), name='club-head-dashboard'),
    
]