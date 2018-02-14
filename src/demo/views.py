# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth import get_user_model
from django.db.models import Prefetch
from django.views import generic

from demo.models import ServiceCategory
from waves.wcore.models import get_service_model
from waves.wcore.views.jobs import JobSubmissionView as CoreDetailView, JobListView as CoreJobListView, Job, \
    JobView as CoreJobView

Service = get_service_model()
User = get_user_model()


class ServiceDetailView(CoreDetailView):
    model = Service
    template_name = 'demo/service_details.html'

    def render_to_response(self, context, **response_kwargs):
        response = super(ServiceDetailView, self).render_to_response(context, **response_kwargs)
        api_user = User.objects.filter(email='demoapiuser@atgc-montpellier.fr')
        if api_user:
            # user_waves =
            response.set_cookie('waves_token', api_user[0].auth_token)
        return response


# Create your views here.
class CategoryDetailView(generic.DetailView):
    context_object_name = 'category'
    model = ServiceCategory
    template_name = 'category/category_details.html'
    context_object_name = 'category'


class CategoryListView(generic.ListView):
    template_name = "category/categories_list.html"
    model = ServiceCategory
    context_object_name = 'online_categories'

    def get_queryset(self):
        return ServiceCategory.objects.filter(category_tools__isnull=False).prefetch_related(
            Prefetch('category_tools',
                     queryset=Service.objects.get_services(user=self.request.user),
                     to_attr="category_public_tools"
                     )
        ).distinct()


class JobListView(CoreJobListView):

    def get_queryset(self):
        api_user = User.objects.filter(email='demoapiuser@atgc-montpellier.fr')
        queryset = Job.objects.filter(client=api_user)
        return queryset


class JobView(CoreJobView):
    pass
