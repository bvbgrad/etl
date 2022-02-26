"""
    Entry point for the application
"""

import app.main.main as app
import app.utils6L.utils6L as utils


if __name__ == '__main__':
    utils.setup_logging()
    app.menu()
