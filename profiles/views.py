from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404
from .models import UserProfile


class ProfileView(TemplateView):
    '''
    View to render the Usre Profile
    '''
    template_name = 'profiles/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Retrieve the user's profile
        profile = get_object_or_404(UserProfile, user=self.request.user)

        # Add the profile to the context
        context['profile'] = profile

        return context
