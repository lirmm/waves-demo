from django.db.models import Prefetch
from django.views import generic
from waves.models import Service

from .models import ServiceCategory


from waves.models import get_service_model

Service = get_service_model()

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
