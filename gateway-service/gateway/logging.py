import logging
import os
from pathlib import Path

# Get the base directory (gateway-service)
BASE_DIR = Path(__file__).parent.parent
LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(exist_ok=True)

# Create logger
logger = logging.getLogger('gateway')
logger.setLevel(logging.INFO)

# Prevent propagation to root logger
logger.propagate = False

# Remove existing handlers to avoid duplicates
if logger.handlers:
    logger.handlers.clear()

# Create formatter
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s", 
                            datefmt="%Y-%m-%d %H:%M:%S")

# File handler - write to logs/gateway.log
log_file = LOGS_DIR / "gateway.log"
file_handler = logging.FileHandler(log_file, encoding='utf-8')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)

# Add handlers
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# Test log to verify it's working
logger.info("Logging initialized successfully")

