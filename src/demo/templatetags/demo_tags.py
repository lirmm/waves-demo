from __future__ import unicode_literals

from django import template
from demo import __version_detail__

register = template.Library()


@register.simple_tag
def get_demo_name():
    return "WAVES DEMO APPLICATION"

@register.simple_tag
def get_demo_version():
    return __version_detail__


@register.inclusion_tag('demo/run_details.html', takes_context=False)
def job_run_details(job=None):
    if job is not None and job.run_details is not None:
        return {'run_details': vars(job.run_details).items()}
    else:
        return {'run_details': {'N/A': 'Unknown'}}
