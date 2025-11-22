from django.shortcuts import redirect
from django.http import HttpResponseRedirect

def root_view(request):
    """Root view that redirects based on authentication"""
    if request.user.is_authenticated:
        # Check if user has is_admin attribute (Employee model)
        try:
            if hasattr(request.user, 'is_admin') and request.user.is_admin:
                return HttpResponseRedirect('/dashboard/')
            else:
                return HttpResponseRedirect('/dashboard/employee/')
        except:
            return HttpResponseRedirect('/accounts/login/')
    else:
        return HttpResponseRedirect('/accounts/login/')

