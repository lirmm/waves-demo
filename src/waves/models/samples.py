from django.db import models

from waves.utils import service_sample_directory


class ServiceInputSample(models.Model):
    class Meta:
        ordering = ['name']
        db_table = 'waves_service_sample'
        unique_together = ('name', 'input', 'service')

    name = models.CharField('File name', max_length=200, null=False)
    file = models.FileField('File path', upload_to=service_sample_directory, null=True, blank=True)
    input = models.ForeignKey('ServiceInput', on_delete=models.CASCADE, related_name='input_samples',
                              help_text='Associated input')
    service = models.ForeignKey('Service', on_delete=models.CASCADE, related_name='services_sample', null=True)
    dependent_input = models.ForeignKey('ServiceInput',
                                        on_delete=models.SET_NULL, null=True, blank=True,
                                        help_text='Dependent on another input value')
    when_value = models.CharField('Depending on input value', max_length=255, null=True, blank=True,
                                  help_text='For dependency, related value')


