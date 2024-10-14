# logger configuration for the project
"""
Module setting up loggers.

In case of unexpected errors handling use general block with 'logger' shown below:
It passes short info about error to user, but not shown specified data.

except Exception as e:
    print(f"An unexpected error occurred.")
    logger.error(e, exc_info=True)


In case of expected errors use rather specified error handling and then use block with 'logger_withDisplay':
This will pass log to file, but also displays error description.
f.e.

except TypeError as err:
    log_msg = (f"Wrong type provided: {err}")
    logger_withDisplay.warning(log_msg)

"""

import logging

# file handler for error logs (only ERROR and CRITICAL)
file_handler_error = logging.FileHandler('logs_error.log')
file_handler_error.setLevel(logging.ERROR)
format_file = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler_error.setFormatter(format_file)

# file handler for warning logs (WARNINGS only)
file_handler_warning = logging.FileHandler('logs_warning.log')
file_handler_warning.setLevel(logging.WARNING)
file_handler_warning.addFilter(lambda record: record.levelno == logging.WARNING)  # add filter to retrieve only WARNINGS
file_handler_warning.setFormatter(format_file)

# file handler for info logs
file_handler_info = logging.FileHandler('logs_info.log')
file_handler_info.setLevel(logging.INFO)
file_handler_info.addFilter(lambda record: record.levelno == logging.INFO)
file_handler_info.setFormatter(format_file)

# console display handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
format_console = logging.Formatter('%(message)s')
console_handler.setFormatter(format_console)


# LOGGER definition (logs saved in file only)
logger = logging.getLogger('basic_logger')
logger.setLevel(logging.DEBUG)
logger.addHandler(file_handler_error)  # add error file handler
logger.addHandler(file_handler_warning)  # add warning file handler
logger.addHandler(file_handler_info)  # add info file handler
logger.addHandler(file_handler_error)  # add file handler only


# LOGGER WITH DISPLAY definition (logs saved both in file and displayed in console)
logger_withDisplay = logging.getLogger('complex_logger')
logger_withDisplay.setLevel(logging.DEBUG)
logger_withDisplay.addHandler(file_handler_error)  # add error file handler
logger_withDisplay.addHandler(file_handler_warning)  # add warning file handler
logger_withDisplay.addHandler(file_handler_info)  # add info file handler
logger_withDisplay.addHandler(console_handler)  # add console handler


