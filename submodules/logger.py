__author__ = 'Roland'

from logging import getLogger, StreamHandler, Formatter
from logging import ERROR, INFO

GENERAL_MESSAGE = '%(message)s'
DETAILED_MESSAGE = '%(asctime)-15s --- %(levelname)-6s : %(message)s'

_LOGGER = None


def prepare_logger(verbosity):
    """
    setup the logger
    :param verbosity: determines how much information the logger is to show
    :return:
    """
    global _LOGGER
    if verbosity == 0:
        return
    else:
        _LOGGER = getLogger('youtube_user_graph')
        _LOGGER.verbosity = verbosity
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
    """
    makes the logger show an error message
    :param message: the error message to show
    :return:
    """
    if _LOGGER is not None:
        _LOGGER.error(message)


def declare_degree(degree):
    """
    make logger show the current degree
    :param degree: the degree to show
    :return:
    """
    if _LOGGER is not None:
        if _LOGGER.verbosity >= 2:
            _LOGGER.info('Degree: #{}'.format(degree))


def declare_processed_users(user_count):
    """
    make logger show the number of processed users
    :param user_count: how many users have been processed.
    :return:
    """
    if _LOGGER is not None:
        if _LOGGER.verbosity >= 2:
            _LOGGER.info('Users Processed: {}'.format(user_count))


def declare_new_node(node):
    """
    make logger show that a new node has been added
    :param node: the new node
    :return:
    """
    if _LOGGER is not None:
        if _LOGGER.verbosity >= 3:
            _LOGGER.info('New Node: {}'.format(node))


def declare_new_edge(edge_start, edge_end):
    """
    make logger show that a new edge has been added
    :param edge_start: the first node in the edge
    :param edge_end: the last node in the edge
    :return:
    """
    if _LOGGER is not None:
        if _LOGGER.verbosity >= 3:
            _LOGGER.info('New Edge: {} to {}'.format(edge_start, edge_end))







