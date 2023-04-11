from django.conf import settings

def bag_contents(request):

    context = {'free_delivery_threshold': settings.FREE_DELIVERY_THRESHOLD,}

    return context