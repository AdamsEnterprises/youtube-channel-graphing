__author__ = 'Roland'

import urllib as urlmanager

try:
    urlmanager.urlopen
except AttributeError:
    from urllib import request as urlmanager

import itertools
import random
import logging
import multiprocessing
#  from Queue import Empty as EmptyQueueException

import networkx
import bs4

random.seed(-1)

DEBUG = True

# TODO add argpharsing for CLI usage.


# Argparse:
#       first user url,     degrees of separation,  [first user name]
#       [output file name, write graph data to file.]
#       [output to console]
#       [verbosity (info level logging)
#           0 (default, always) - errors
#           1 - low: current degree, number of users processed
#           2 - medium: adding of nodes, edges
#           3 - high: discovery of colleagues, current processing time, estimated remaining time.]
#
#           never shown: debugging logging.


# what do we do with the next user? find colleagues and add user to the nodes.
# what do we do when we find colleagues? add them to the queue if they are not in the queue.
# what do we do if next user already is in nodes? skip it.
# what do we do if a colleague is already in the nodes? add an edge from user to colleague.
# what do we do when degree is below max? do all of the above.
# what do we do when degree matches max? don't add colleagues to the queue.


# start with default only in queue.
# for each degree:
#   for next user in queue:
#       if user is in nodes?
#           skip user, continue
#       else
#           add the user to the nodes
#           grab the user's colleagues
#           for each colleague
#               if colleague is in nodes?
#                   add edge from user to colleague
#               else if degree < max-degree
#                   add colleague to queue
#       degree += 1


# important constants, for web scraping
URL_YOUTUBE_USER = u'https://www.youtube.com'
SUBURL_YOUTUBE_CHANNELS = u'/channels?view=60'
RELATED_CHANNELS_TAG = 'li'
RELATED_CHANNELS_CLASS_ATTR_VALUE = 'channels-content-item yt-shelf-grid-item'
RELATED_CHANNEL_TAG_NAME = 'h3'

# defaults
DEFAULT_FIRST_USER = (u'Cryaotic', URL_YOUTUBE_USER +
                      u'/channel/UCu2yrDg7wROzElRGoLQH82A' + SUBURL_YOUTUBE_CHANNELS)
DEFAULT_MAX_DEGREES_OF_SEPARATION = 1

# for debugging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)-15s ### %(filename)-15s' +
                              ' - %(lineno)-5d ::: %(levelname)-6s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

# global script objects
graph_nodes = networkx.Graph()


# Resources shared between Processes
user_queue = multiprocessing.Queue()
users_processed = list()
users_to_do = list()


def get_association_list(url):
    # grab the webpage at the given url

    strainer = bs4.SoupStrainer(RELATED_CHANNELS_TAG,
                                attrs={'class': RELATED_CHANNELS_CLASS_ATTR_VALUE})

    # scrape the tags representing related channels
    channels = bs4.BeautifulSoup(urlmanager.urlopen(url), 'html.parser', parse_only=strainer)

    ret_list = list()

    for channel in channels:
        if not isinstance(channel, bs4.Tag):
            continue
        # channel name is text in form "<name> <delimiter> Channel", we want only <name>.
        try:
            element = channel.find(RELATED_CHANNEL_TAG_NAME)
            element_anchor = element.a
            user_name = element_anchor['title']
            link = URL_YOUTUBE_USER + element_anchor['href'] + SUBURL_YOUTUBE_CHANNELS
        except (KeyError, AttributeError):
            logger.error('Could not parse HTML element on this page, may be malformed: ' + str(url))
            continue
        listing = (user_name, link)
        ret_list.append(listing)

    return ret_list


def generate_colours(degree):
    if not isinstance(degree, int):
        raise TypeError("Parameter 'degree' must be Integer.")
    if degree <= 0:
        raise ValueError("Parameter 'degree' must be greater than or equal to 1.")
    color_list = list()
    # get list of all possible colours.
    colors = list()
    # for x colours required, there are x^3-2 colours produced
    x = 2
    # rnumber of degrees is (0, ..., n) thus number of colours returned = n + 1
    while degree + 1 > ((x * x * x) - 2):
        x += 1
    scale_factor = int((256.0 / (x - 1) - 0.1))
    scale = range(0, 256, scale_factor)
    for i in itertools.product(scale, scale, scale):
        # convert from (R, G, B)decimal to '#RRGGBB'hex
        c = '#' + hex(i[0])[2:].zfill(2) + hex(i[1])[2:].zfill(2) + hex(i[2])[2:].zfill(2)
        colors.append(c)
    # dump existing colours, and black and white
    del colors[0]
    del colors[-1]
    # create list of colours, unique per degree of separation
    for i in range(degree + 1):
        x = random.randint(0, len(colors) - 1)
        color_list.append(colors[x])
        del colors[x]

    return color_list


def generate_graph():
    if DEBUG:
        logger.debug('Generating graph now...')

    graph_nodes.clear()

    degree = 0
    users_to_do.append(DEFAULT_FIRST_USER)
    graph_nodes.add_node(DEFAULT_FIRST_USER[0], degree=degree)
    if DEBUG:
        logger.debug('new graph node - ' + DEFAULT_FIRST_USER[0])

    degree += 1

    while degree <= DEFAULT_MAX_DEGREES_OF_SEPARATION:
        if DEBUG and degree <= DEFAULT_MAX_DEGREES_OF_SEPARATION:
            logger.debug('new degree: ' + str(degree) + ' #######')

        while len(users_to_do) > 0:
            user_queue.put(users_to_do.pop())

        if DEBUG and user_queue.qsize() > 0:
            logger.debug('user queue size - ' + str(user_queue.qsize()))

        while True:

            if DEBUG:
                logger.debug('Entered queue processing.')

            # unload the next users from the queue.
            if user_queue.empty() or user_queue.qsize() < 1:
                # ran out of next_users - stop analyzing this level
                if DEBUG:
                    logger.debug('about to end queue processing.')
                break

            user_name, url = user_queue.get()
            # list of (name, url) tuples with edge to this user url.
            associations = get_association_list(url)
            if DEBUG:
                logger.debug('retrieved associations.')
            for colleague in associations:
                colleague_name, _ = colleague
                if not graph_nodes.has_node(colleague_name):
                    graph_nodes.add_node(colleague_name, degree=degree)
                    if DEBUG:
                        logger.debug('new graph node - ' + colleague_name)
                if not graph_nodes.has_edge(user_name, colleague_name) or \
                        graph_nodes.has_edge(colleague_name, user_name):
                    graph_nodes.add_edge(user_name, colleague_name)
                    if DEBUG:
                        logger.debug('new edge - ' + user_name + ', ' + colleague_name)
                if degree < DEFAULT_MAX_DEGREES_OF_SEPARATION \
                        and colleague not in users_processed \
                        and colleague not in users_to_do:
                    users_to_do.append(colleague)

            users_processed.append((user_name, url))
            if DEBUG:
                logger.debug('processed users - ' + str(len(users_processed)))

        degree += 1

    return


def show_graph():
    colors = generate_colours(DEFAULT_MAX_DEGREES_OF_SEPARATION)
    networkx.draw_spring(graph_nodes,
                         node_color=[colors[graph_nodes.node[node]['degree']]
                                     for node in graph_nodes])

    return


if __name__ == '__main__':
    generate_graph()
    show_graph()
