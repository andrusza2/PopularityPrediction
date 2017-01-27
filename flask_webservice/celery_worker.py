#!/usr/bin/env python
"""
Module used for starting celery-worker.
"""

import os
from app import celery, create_app

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
app.app_context().push()
