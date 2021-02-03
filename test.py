import pexpect
import re
import json
from worker import worker
w = worker()
data = w.checkMessagePool()
w.processMessage(data)
