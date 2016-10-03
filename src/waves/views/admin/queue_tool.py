"""
Ajax loaded view to relaunch a failed queue daeman

"""
from django.views.generic import FormView, View


class DaemonToolView(View):
    """
    Daemon tool view, called in ajax to launch action o WAVES queue process

    """
    pass