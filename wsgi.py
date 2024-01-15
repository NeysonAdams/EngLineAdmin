import sys

path = '/home/khamraeva/mysite/EngLineAdmin'

if path not in sys.path:
   sys.path.insert(0, path)

from main import app as application