from __future__ import unicode_literals

import swapper
from django.db.models import Prefetch
from django.views import generic

from demo.models import ServiceCategory
from waves.wcore.models import get_service_model
from waves.front.views import ServiceDetailView as CoreDetailView

Service = get_service_model()


class ServiceDetailView(CoreDetailView):
    model = Service
    template_name = 'demo/service_details.html'


# Create your views here.
class CategoryDetailView(generic.DetailView):
    context_object_name = 'category'
    model = ServiceCategory
    template_name = 'category/category_details.html'
    context_object_name = 'category'

    def get_queryset(self):
        return ServiceCategory.objects.all().prefetch_related(
            Prefetch('category_tools',
                     queryset=Service.objects.get_web_services(user=self.request.user),
                     to_attr="category_public_tools"
                     )
        )


class CategoryListView(generic.ListView):
    template_name = "category/categories_list.html"
    model = ServiceCategory
    context_object_name = 'online_categories'

    def get_queryset(self):
        return ServiceCategory.objects.all().prefetch_related(
            Prefetch('category_tools',
                     queryset=Service.objects.get_web_services(user=self.request.user),
                     to_attr="category_public_tools"
                     )
        )
