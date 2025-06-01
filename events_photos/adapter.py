from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.core.exceptions import ValidationError
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from django.http import HttpResponseRedirect
from allauth.exceptions import ImmediateHttpResponse

class SchoolAccountAdapter(DefaultAccountAdapter):
    pass

class SchoolSocialAccountAdapter(DefaultSocialAccountAdapter):
    # Define your school's email domain here.
    SCHOOL_EMAIL_DOMAIN = 'kld.edu.ph' # REPLACE THIS with your actual school email domain!

    def pre_social_login(self, request, sociallogin):
        """
        Invoked just prior to the social login process.
        Here we can check the email domain.
        """
        # Ensure the email is available and from the social provider
        if sociallogin.email_addresses:
            email = sociallogin.email_addresses[0].email
            domain = email.split('@')[1]
            if domain != self.SCHOOL_EMAIL_DOMAIN:
                # This will raise a ValidationError and prevent the login/signup
                # You can customize the error message to be more user-friendly
                request.session['kld_email_error'] = (
                    f"Authentication failed: Please use your {self.SCHOOL_EMAIL_DOMAIN} Google Account to sign in."
                )
                raise ImmediateHttpResponse(redirect(reverse('home')))
                
        return None

    def is_auto_signup_allowed(self, request, sociallogin):
        """
        If `AUTO_SIGNUP` is True, this method determines if a new user can be
        automatically signed up. We already filtered by domain in `pre_social_login`.
        """
        return True # Allows automatic signup after passing domain check

    def get_login_redirect_url(self, request):
        """
        Return the URL to redirect to after a successful login (social or otherwise).
        This overrides LOGIN_REDIRECT_URL from settings for more dynamic control.
        """
        # For our case, we'll just use the LOGIN_REDIRECT_URL from settings.
        # This method is more useful if you have complex redirect logic.
        return reverse('home')

    def authentication_error(self, request, provider_id, error=None, **kwargs):
        
        if error and 'access_denied' in str(error).lower() and self.SCHOOL_EMAIL_DOMAIN in str(error).lower():
            request.session['kld_email_error'] = f"Authentication failed: Please use your {self.SCHOOL_EMAIL_DOMAIN} Google Account to sign in."
        elif error:
            request.session['kld_email_error'] = "An authentication error occurred. Please try again."
        
        return redirect(reverse('home'))
