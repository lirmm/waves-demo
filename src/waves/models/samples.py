from __future__ import unicode_literals

from django.db import models
from waves.models.storage import waves_storage
from waves.models.base import OrderAble


def service_sample_directory(instance, filename):
    return 'sample/{0}/{1}'.format(instance.service.api_name, filename)


class ServiceInputSample(models.Model):
    class Meta:
        ordering = ['name']
        db_table = 'waves_service_sample'
        unique_together = ('name', 'input', 'service')

    name = models.CharField('Name', max_length=200, null=False)
    file = models.FileField('File', upload_to=service_sample_directory, storage=waves_storage)
    input = models.ForeignKey('ServiceInput', on_delete=models.CASCADE, related_name='input_samples',
                              help_text='Associated input')
    service = models.ForeignKey('Service', on_delete=models.CASCADE, related_name='services_sample', null=True)


class ServiceSampleDependentsInput(OrderAble):
    class Meta:
        db_table = 'waves_sample_dependent_input'

    sample = models.ForeignKey(ServiceInputSample, on_delete=models.CASCADE)
    dependent_input = models.ForeignKey('ServiceInput', on_delete=models.CASCADE)
    set_value = models.CharField('When sample selected, set value to ', max_length=200, null=False, blank=False)

