import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'contrib'))

import sae
from entry import webapp

application = sae.create_wsgi_app(webapp.wsgifunc())