* `django.log`: Contains logs by Django framework like executed SQL statements
* `process_queue.log`: Contains logs for job processing errors traces 
* `waves.log`: Contains logs from the `waves` web application logger. For example:

		# At the top of your file/module
		import logging
		logger = logging.getLogger(__name__)

		# Anywhere else in the file
		logger.info('Started processing foo')
