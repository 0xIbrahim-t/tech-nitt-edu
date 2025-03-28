from django.views.generic import View
from api.controllers.response_format import error_response
from django.contrib.auth import authenticate, login
from api.controllers.user_utilities import *
from api.utils import utils
from django.shortcuts import redirect
from api.utils.utils import *
from api.models import User
from api.decorators.response import JsonResponseDec
from django.utils.decorators import method_decorator
from django.core.files.storage import FileSystemStorage
import logging

logger = logging.getLogger(__name__)

@method_decorator(JsonResponseDec, name='dispatch')
class LoginFormView(View):
    def post(self, req):
        """
        Logs in the user and sets session
        """
        email = req.POST.get('email')
        password = req.POST.get('password')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return error_response("User does not exist")
        
        # if user.is_verified:
        #     user = authenticate(username=email, password=password)
        # else:
        #     logger.info('User(email={}) Verification pending'.format(email))
        #     return error_response("Email verification pending. Please check your inbox to activate your account")
        
        user = authenticate(username=email, password=password)
        if user is not None:
            remove_existing_sessions(user.id)
            req.session['user_id'] = user.id
            login(req, user)
            response = {'email': user.email, 'name': user.name,}
            logger.info('{} Login successful'.format(user))
            return response
        else:
            logger.info('User(email={}) Password incorrect'.format(email))
            return error_response("User password incorrect")

@method_decorator(JsonResponseDec, name='dispatch')
class LogoutView(View):
    def post(self, req):
        """
        Logs out user by deleting his session
        """
        user = req.session.get('user_id')

        if user is not None:
            del req.session['user_id']
            logger.info('{} Logged out successfully'.format(user))
            return "Logged out successfully!"
        else:
            logger.info('{} Logout error'.format(user))
            return error_response("Logout error!")

@method_decorator(JsonResponseDec, name='dispatch')
class RegisterFormView(View):
    def post(self, req):
        """
        If the credentials are in proper format and email doesn't already exist, register a user
        """
        email = req.POST.get('email')
        print(email)
        password = req.POST.get('password')
        name = req.POST.get('name')
        is_admin = False

        myfile = req.FILES['profile_pic']
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        uploaded_file_url = fs.url(filename)
        print(uploaded_file_url)
        
        if "@nitt.edu" not in email:
            return error_response("Please use webmail")
        
        if validate_email(email) and len(password) >= 8 and name is not None:
            print(f"this is the email {email} - {admin_mail}")
            if email in admin_mail:
                is_admin = True
            if not User.objects.filter(email=email).exists():
                register_user(email, name, password, uploaded_file_url, is_admin)
                logger.info('User(webmail={}) Registration successful'.format(email))
                return "Registration Successful!"
            else:
                logger.info('User(webmail={}) Account already exists'.format(email))
                return error_response("An account already exists under the webmail address")
        else:
            logger.info('email={} Invalid user details')
            return error_response("Invalid user details")

class ResetPassRequest(View):
    def post(self, req):
        """Get email from post request.
            Check if the user exists and is verified.
            Then send reset password link to user"""
        email = req.POST.get('email')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return error_response("User does not exist")
        
        if user.is_verified:
            #TODO make function to send reset password link
            send_reset_pass_link(user)
            logger.info('User(email={}) Password reset link sent'.format(email))
            return "Password reset link sent!"
        else:
            logger.info('User(email={}) Verification pending'.format(email))
            return error_response("Email verification pending. Please check your inbox to activate your account")

class ResetPassUpdate(View):
    def post(self, req):
        pass


@method_decorator(JsonResponseDec, name='dispatch')
class IsLoggedInView(View):
    def get(self, req):
        """
        Checks if the user is logged in.
        Returns user details if logged in, otherwise indicates the user is not logged in.
        """
        user_id = req.session.get('user_id')
        if user_id:
            try:
                user = User.objects.get(id=user_id)
                logger.info(f"User {user.email} is logged in.")
                if user.email in utils.admin_mail:
                    return {"loggedIn": True, "isAdmin": True, "email": user.email, "name": user.name}
                else:
                    return {"loggedIn": True, "isAdmin": False, "email": user.email, "name": user.name}
            except User.DoesNotExist:
                logger.warning("Session user not found in database.")
                # Clear session if user doesn't exist
                req.session.pop('user_id', None)
                return {"loggedIn": False, "error": "User does not exist."}
        else:
            return {"loggedIn": False}
        


class UserRedirectView(View):
    def get(self, request):
        user_id = request.session.get('user_id')
        print(utils.admin_mail)

        if not user_id:
            logger.info("User not logged in, redirecting to home.")
            return redirect('/')

        try:
            user = User.objects.get(id=user_id)

        except User.DoesNotExist:
            logger.warning("User not found in database, clearing session and redirecting to home.")
            request.session.pop('user_id', None)
            return redirect('/')

        if user.email in utils.admin_mail:  # Assuming this field exists in your model
            logger.info(f"User {user.email} is an overall admin, redirecting to Technical Council.")
            return redirect('/admin/technicalcouncil')
        
        else:  # Assuming this field exists in your model
            logger.info(f"User {user.email} is a club head, redirecting to Club Heads.")
            return redirect('/admin/clubheads')