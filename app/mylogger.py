import logging

# Make a global logging object.
logger = logging.getLogger("mylogger")
logger.setLevel(logging.DEBUG)
h = logging.StreamHandler()
f = logging.Formatter("%(levelname)s %(asctime)s %(funcName)s %(lineno)d %(message)s")
h.setFormatter(f)
logger.addHandler(h)

