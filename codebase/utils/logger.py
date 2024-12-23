import logging

class CustomFormatter(logging.Formatter):
    """Custom logging formatter to add colors to log levels."""
    
    COLORS = {
        logging.DEBUG: "\033[94m",  # Blue
        logging.INFO: "\033[95m",   # Magenta
        logging.ERROR: "\033[91m",  # Red
        'RESET': "\033[0m"    # Reset color
    }

    def format(self, record):
        log_color = self.COLORS.get(record.levelno, self.COLORS['RESET'])
        reset_color = self.COLORS['RESET']
        record.msg = f"{log_color}{record.msg}{reset_color}"
        return super().format(record)

def get_logger(name):
    """Create and configure a logger with the given name."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    formatter = CustomFormatter('[Logger] - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)

    logger.addHandler(ch)
    return logger