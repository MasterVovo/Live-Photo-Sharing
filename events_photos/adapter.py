from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.core.exceptions import ValidationError

class SchoolAccountAdapter(DefaultAccountAdapter):
    # This adapter will be used for general account behavior (e.g., if you had local signups)
    # but the social adapter is more relevant for social logins.
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
                raise ValidationError(
                    f"Access denied: You must use an email address from {self.SCHOOL_EMAIL_DOMAIN} to log in."
                )

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
        from django.conf import settings
        return settings.LOGIN_REDIRECT_URL