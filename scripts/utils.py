"""Utility functions and classes."""

import logging

all = ["LoggerFormatter"]


class LoggerFormatter(logging.Formatter):
    """Fancy color formatter for logging messages."""
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    PALEGRAY = '\033[38;5;245m'
    RESET = '\033[0m'

    def format(self, record):
        levelname = record.levelname
        padded_name = f"{levelname:<5}"  # Left aligned, padded to 8 chars
        if levelname == 'INFO':
            record.levelname = f'{self.BLUE}{padded_name}{self.RESET}'
        elif levelname == 'WARNING':
            record.levelname = f'{self.YELLOW}{padded_name}{self.RESET}'
        elif levelname == 'ERROR':
            record.levelname = f'{self.RED}{padded_name}{self.RESET}'
        elif levelname == 'DEBUG':
            record.levelname = f'{padded_name}' # No color change

        funcName = record.funcName
        funcName = f"{funcName:<12.12}"
        record.funcName = f'{self.PALEGRAY}{funcName}{self.RESET}'
        return super().format(record)