#!/usr/bin/env python
"""
Utility for starting webservice
"""

import os
from app import create_app

app = create_app(os.getenv('FLASK_CONFIG') or 'default')

if __name__ == '__main__':
    app.run(debug=False, threaded=True, host='0.0.0.0')
