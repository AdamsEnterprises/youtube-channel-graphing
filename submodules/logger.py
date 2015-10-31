__author__ = 'Roland'

from logging import getLogger, StreamHandler, Formatter
from logging import ERROR, INFO

GENERAL_MESSAGE = '%(message)s'
DETAILED_MESSAGE = '%(asctime)-15s --- %(levelname)-6s : %(message)s'

_LOGGER = None


def prepare_logger(verbosity):
    global _LOGGER
    if verbosity == 0:
        return
    else:
        _LOGGER = getLogger('youtube_user_graph')
        if verbosity == 1:
            _LOGGER.setLevel(ERROR)
            formatter = Formatter(GENERAL_MESSAGE)
        else:
            _LOGGER.setLevel(INFO)
            if verbosity >= 4:
                formatter = Formatter(DETAILED_MESSAGE)
            else:
                formatter = Formatter(GENERAL_MESSAGE)
        console_handler = StreamHandler()
        console_handler.setFormatter(formatter)
        _LOGGER.addHandler(console_handler)
    return


def declare_error(message):
    _LOGGER.error(message)


def declare_degree(degree):
    _LOGGER.info('Degree: #{}'.format(degree))


def declare_processed_users(user_count):
    _LOGGER.info('Users Processed: {}'.format(user_count))


def declare_new_node(node):
    _LOGGER.info('New Node: {}'.format(node))


def declare_new_edge(edge_start, edge_end):
    _LOGGER.info('New Edge: {} to {}'.format(edge_start, edge_end))







