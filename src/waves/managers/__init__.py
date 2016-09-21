__author__      = 'Marc Chakiachvili, LIRMM Laboratory'
__copyright__   = "Copyright 2016, LIRMM"
__license__     = "MIT"

from cron import treat_queue_jobs, purge_old_jobs
from mails import JobMailer
from servicejobs import ServiceJobManager
