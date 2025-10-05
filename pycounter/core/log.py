import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QtMsgType

def setup_logging(
        filename: str | None = None, 
        max_bytes: int = 5_000_000,
        backup_count: int = 5
    ):
    """
    Sets up logging for the PyCounter application.

    - Logs to ~/.pycounter/pycounter.log by default
    - Also logs to stdout
    - Prevents duplicate handlers
    """

    if not filename:
        logfile = Path.home().joinpath('.pycounter').joinpath('pycounter.log')
        logfile.parent.mkdir(mode=0o777, parents=True, exist_ok=True)
    else:
        logfile = Path(filename)

    fmt = logging.Formatter(
        fmt="%(asctime)s-[%(levelname)s]-%(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    logger = logging.getLogger('pycounter')
    logger.setLevel(logging.DEBUG)
    
    if not logger.handlers:

        filehandler = RotatingFileHandler(
            str(logfile), 
            mode='a', 
            encoding='latin-1',
            maxBytes=max_bytes,
            backupCount=backup_count
        )
        filehandler.setFormatter(fmt)

        streamhandler = logging.StreamHandler()
        streamhandler.setFormatter(fmt)

        logger.addHandler(filehandler)
        logger.addHandler(streamhandler)

    return logger

def exception_hook(exc_type, exc_value, exc_traceback):
    """Global exception hook to catch unhandled exceptions."""
    logging.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

    # Show user-friendly message box
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Critical)
    msg.setWindowTitle("Unexpected Error")
    msg.setText("An unexpected error occurred.\nSee log for details.")
    msg.setStandardButtons(QMessageBox.Ok)
    msg.exec_()

def qt_message_handler_wrapper(logger: logging.Logger):
    def qt_message_handler(mode, context, message):
        """Optional: Redirect Qt internal warnings/errors to logging."""
        levels = {
            QtMsgType.QtInfoMsg: logger.info,
            QtMsgType.QtWarningMsg: logger.warning,
            QtMsgType.QtCriticalMsg: logger.error,
            QtMsgType.QtFatalMsg: logger.critical,
        }
        log_func = levels.get(mode, logger.info)
        log_func(f"Qt: {message}")
        
    return qt_message_handler

logger = setup_logging()  
    
