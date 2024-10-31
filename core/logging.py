"""Core logging configuration for the application"""
import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional, Dict, Any
import json
from datetime import datetime

from core.config import settings

class SafeJSONFormatter(logging.Formatter):
    """Custom JSON formatter that handles reserved keywords"""
    
    RESERVED_ATTRS = {
        'args', 'asctime', 'created', 'exc_info', 'exc_text', 'filename',
        'funcName', 'levelname', 'levelno', 'lineno', 'module', 'msecs',
        'msg', 'name', 'pathname', 'process', 'processName', 'relativeCreated',
        'stack_info', 'thread', 'threadName'
    }
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON, safely handling reserved keywords"""
        # Create base log data
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage()
        }
        
        # Add extra fields if available, avoiding reserved keywords
        if hasattr(record, 'extra'):
            extras = {}
            for key, value in record.extra.items():
                # If key is reserved, prefix it
                if key in self.RESERVED_ATTRS:
                    extras[f"extra_{key}"] = value
                else:
                    extras[key] = value
            log_data.update(extras)
            
        # Add exception info if available
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
            
        return json.dumps(log_data)

def setup_logging() -> None:
    """Configure application logging"""
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Create formatters
    json_formatter = SafeJSONFormatter()
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Clear any existing handlers
    root_logger.handlers = []
    
    # Create handlers for different log levels
    handlers = {
        # Error logs (ERROR and above)
        "error": logging.handlers.RotatingFileHandler(
            log_dir / "error.log",
            maxBytes=10_485_760,  # 10MB
            backupCount=5
        ),
        # Application logs (INFO and above)
        "app": logging.handlers.RotatingFileHandler(
            log_dir / "app.log",
            maxBytes=10_485_760,
            backupCount=5
        ),
        # Debug logs (if debug mode)
        "debug": logging.handlers.RotatingFileHandler(
            log_dir / "debug.log",
            maxBytes=10_485_760,
            backupCount=3
        ) if settings.DEBUG else None,
        # Console output
        "console": logging.StreamHandler(sys.stdout)
    }
    
    # Configure handlers
    handlers["error"].setLevel(logging.ERROR)
    handlers["app"].setLevel(logging.INFO)
    if handlers["debug"]:
        handlers["debug"].setLevel(logging.DEBUG)
    handlers["console"].setLevel(logging.INFO if not settings.DEBUG else logging.DEBUG)
    
    # Add formatters
    for handler in handlers.values():
        if handler:
            handler.setFormatter(json_formatter)
    
    # Add handlers to root logger
    for handler in handlers.values():
        if handler:
            root_logger.addHandler(handler)
    
    # Configure specific loggers
    loggers = {
        "httpx": logging.WARNING,
        "httpcore": logging.WARNING,
        "hpack": logging.WARNING,
        "langchain": logging.INFO,
        "supabase": logging.INFO
    }
    
    for logger_name, level in loggers.items():
        logging.getLogger(logger_name).setLevel(level)

# Initialize logging when module is imported
setup_logging()

# Export the get_logger function
def get_logger(name: str) -> logging.Logger:
    """Get a logger instance"""
    return logging.getLogger(name)