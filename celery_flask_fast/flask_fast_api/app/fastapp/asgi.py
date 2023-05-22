import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
import uvicorn
from fastapp.main import fast_app

if __name__ == "__main__":
    uvicorn.run(fast_app, host='0.0.0.0', port=8081)
