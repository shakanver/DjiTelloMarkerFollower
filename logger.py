import logging

logging.basicConfig(filename='log.txt',
					format='(%(asctime)s] [%(levelname)s] %(message)s',
					filemode='w')

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
