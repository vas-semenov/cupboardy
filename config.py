import logging


class Config:
    SECRET_KEY = 'TemporarySecretKey'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    LOGGING_LEVEL = logging.DEBUG
