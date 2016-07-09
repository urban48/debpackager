LOG_CONF = {
    'version': 1,
    'disable_existing_loggers': False,
    'loggers':
        {
            '': {
                'handlers': ['console'],
                'level': 'DEBUG',
            },
        },

    'handlers': {
        # 'file': {
        #     "class": "logging.handlers.RotatingFileHandler",
        #     "level": "DEBUG",
        #     'formatter': 'default',
        #     "filename": "test_run.log",
        # },
        'console': {
            "class": "logging.StreamHandler",
            "level": "INFO",
            'formatter': 'default',
            "stream": "ext://sys.stdout"
        },
    },

    'formatters': {
        'default': {
            'format': '%(message)s'
        },
    }
}
