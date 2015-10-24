"""
Main script for tge youtube graphing project.
"""

__author__ = 'Roland'

import urllib as urlmanager

try:
    # pylint: disable=no-member
    urlmanager.urlopen
except AttributeError:
    #pylint: disable=no-member
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
# -u --url      <url to featured channel list>
#           test:   url actually leads to valid featured channel webpage
#           test:   url is no null
#
# [-d --degrees]    <degrees of separation>
#           ( if not specified, assume 1 degree.)
#           test: degrees is not null
#           test: degrees is an integer greater than 0.
# [-n --name]   <name to attach to origin node>
#           (if no name supplied, must generate name from featured channel webpage, only.)
#           test:   name is not null
#           test:   name is not null if not specified in options.
# [-f -filename]    <file to write output graph data into>
#           test:   filename is not null
#           test:   filename is valid for underlying system.
#           test:   produced file is not empty
#           test:   produced file has expected nodes and edges
#               cases:          <no nodes, no edges>
#                               <1 node, no edges>
#                               <2 nodes, 0 edges>
#                               <2 nodes, 1 edge>
#                               <3 nodes, 0 edges>
#                               <3 nodes, 1 edge>
#                               <3 nodes, 2 edges>
#                               <7 nodes, 0 edges>
#                               <7 nodes, 1 edge>
#                               <7 nodes, 6 edges, not all nodes linked>
#                               <7 nodes, 6 edges, all nodes linked>
#                               <7 nodes, 21 edges, all nodes linked (max linkage for 7 nodes)>
# [-v --verbosity]  <display info logging to console>
#                   (default - 0: off)
#                   (0: off, 1: errors only, 2: current degree and number of users processed...)
#                   (3: new nodes, new edges, 4: date and time of message
#                       and colleagues discovered.)
#           test:   verbosity level gives correct format response
#           (need to capture logging messages for comparison)
# [-h --help]   <help information on options>
#           test: expected output produced.


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
GLOBAL_LOGGER = logging.getLogger(__name__)
GLOBAL_LOGGER.setLevel(logging.DEBUG)
GLOBAL_LOGGER.internal_handler = logging.StreamHandler()
GLOBAL_LOGGER.internal_handler.setLevel(logging.DEBUG)
GLOBAL_LOGGER.internal_formatter = \
    logging.Formatter('%(asctime)-15s ### %(filename)-15s' +
                      ' - %(lineno)-5d ::: %(levelname)-6s - %(message)s')
GLOBAL_LOGGER.internal_handler.setFormatter(GLOBAL_LOGGER.internal_formatter)
GLOBAL_LOGGER.addHandler(GLOBAL_LOGGER.internal_handler)


def get_association_list(url):
    """
    grab the webpage at the given url
    :param url: the url to retrieve associated channels from.
    :return: a list of (user name, associated channel url).
    """

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
            GLOBAL_LOGGER.error('Could not parse HTML element on this page, ' +
                                'may be malformed: ' + str(url))
            continue
        listing = (user_name, link)
        ret_list.append(listing)

    return ret_list


def generate_colours(value):
    """
    create a list of random colours.
    :param value: an integer influencing how many colours to create
    :return: a list of (value + 1) colours
    """
    if not isinstance(value, int):
        raise TypeError("Parameter 'degree' must be Integer.")
    if value <= 0:
        raise ValueError("Parameter 'degree' must be greater than or equal to 1.")
    color_list = list()
    # get list of all possible colours.
    colors = list()
    # for x colours required, there are x^3-2 colours produced
    factor = 2
    # rnumber of degrees is (0, ..., n) thus number of colours returned = n + 1
    while value + 1 > ((factor * factor * factor) - 2):
        factor += 1
    scale_factor = int((256.0 / (factor - 1) - 0.1))
    scale = range(0, 256, scale_factor)
    for i in itertools.product(scale, scale, scale):
        # convert from (R, G, B)decimal to '#RRGGBB'hex
        code = '#' + hex(i[0])[2:].zfill(2) + hex(i[1])[2:].zfill(2) + hex(i[2])[2:].zfill(2)
        colors.append(code)
    # dump existing colours, and black and white
    del colors[0]
    del colors[-1]
    # create list of colours, unique per degree of separation
    for i in range(value + 1):
        index = random.randint(0, len(colors) - 1)
        color_list.append(colors[index])
        del colors[index]

    return color_list


def generate_graph():
    """
    creates a graphing object representing you tube users and associations.
    :return: a networkX graph object, containg users as nodes and relationships as edges.
    """
    if DEBUG:
        GLOBAL_LOGGER.debug('Generating graph now...')

    # graphing object
    graph_nodes = networkx.Graph()
    graph_nodes.clear()

    # pylint: disable=maybe-no-member
    user_queue = multiprocessing.Queue()
    users_processed = list()
    users_to_do = list()

    degree = 0
    users_to_do.append(DEFAULT_FIRST_USER)
    graph_nodes.add_node(DEFAULT_FIRST_USER[0], degree=degree)
    if DEBUG:
        GLOBAL_LOGGER.debug('new graph node - ' + DEFAULT_FIRST_USER[0])

    degree += 1

    while degree <= DEFAULT_MAX_DEGREES_OF_SEPARATION:
        if DEBUG and degree <= DEFAULT_MAX_DEGREES_OF_SEPARATION:
            GLOBAL_LOGGER.debug('new degree: ' + str(degree) + ' #######')

        while len(users_to_do) > 0:
            user = users_to_do.pop()
            user_queue.put(user)
            if DEBUG and user_queue.qsize() > 0:
                GLOBAL_LOGGER.debug('added user to queue: ' + str(user))

        while True:

            # unload the next users from the queue.
            if DEBUG:
                GLOBAL_LOGGER.debug('Is Queue Empty? :: ' + str(user_queue.empty()))
            if DEBUG and user_queue.qsize() > 0:
                GLOBAL_LOGGER.debug('user queue size :: ' + str(user_queue.qsize()))

            if user_queue.empty() or user_queue.qsize() < 1:
                # ran out of next_users - stop analyzing this level
                if DEBUG:
                    GLOBAL_LOGGER.debug('about to end queue processing for this degree.')
                break

            if DEBUG:
                # make sure logging statements are shown in correct order.
                GLOBAL_LOGGER.internal_handler.flush()

            user_name, url = user_queue.get()
            if DEBUG:
                GLOBAL_LOGGER.debug('retrieved next user: ' + user_name + " :: " + url)
            # list of (name, url) tuples with edge to this user url.
            associations = get_association_list(url)
            if DEBUG:
                GLOBAL_LOGGER.debug('retrieved associations.')
            for colleague in associations:
                colleague_name, _ = colleague
                if not graph_nodes.has_node(colleague_name):
                    graph_nodes.add_node(colleague_name, degree=degree)
                    if DEBUG:
                        GLOBAL_LOGGER.debug('new graph node - ' + colleague_name)
                if not graph_nodes.has_edge(user_name, colleague_name) or \
                        graph_nodes.has_edge(colleague_name, user_name):
                    graph_nodes.add_edge(user_name, colleague_name)
                    if DEBUG:
                        GLOBAL_LOGGER.debug('new edge - ' + user_name + ', ' + colleague_name)
                if degree < DEFAULT_MAX_DEGREES_OF_SEPARATION \
                        and colleague not in users_processed \
                        and colleague not in users_to_do:
                    users_to_do.append(colleague)
                    if DEBUG:
                        GLOBAL_LOGGER.debug('new user to process:' + str(colleague))

            users_processed.append((user_name, url))
            if DEBUG:
                GLOBAL_LOGGER.debug('processed users - ' + str(len(users_processed)))

        degree += 1

    return graph_nodes


if __name__ == '__main__':
    youtube_user_graph = generate_graph()
    colors = generate_colours(DEFAULT_MAX_DEGREES_OF_SEPARATION)
    networkx.draw_spring(youtube_user_graph,
                         node_color=[colors[youtube_user_graph.node[node]['degree']]
                                     for node in youtube_user_graph])
