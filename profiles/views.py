from django.views.generic import TemplateView


class ProfileView(TemplateView):
    ''''
    View to render the Usre Profile
    '''
    template_name = 'profiles/profile.html'
