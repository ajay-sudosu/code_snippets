import sys
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
from flaskapp.main import app as application


if __name__ == "__main__":
    application.run()