
import os
import errno
import logging

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(SCRIPT_DIR, os.pardir))

log_dir = os.path.join(parent_dir, 'logs')
log_file = os.path.join(log_dir, 'app.log')

if not os.path.exists(log_dir):
    try:
        os.makedirs(log_dir)
        os.chmod(log_dir, 0o777)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

if not os.path.exists(log_file):
    with open(log_file, 'a'):
        os.utime(log_file, None)
os.chmod(log_file, 0o666)


logging.getLogger("pyrogram").setLevel(logging.WARNING)
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)  
logging.getLogger("sqlalchemy").setLevel(logging.WARNING)   

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG,
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
error_handler = logging.StreamHandler()
error_handler.setLevel(logging.ERROR)
error_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

logger = logging.getLogger("test_bot")
logger.addHandler(error_handler)