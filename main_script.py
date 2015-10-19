__author__ = 'Roland'

import urllib
import itertools
import random
import logging
import multiprocessing
#  from Queue import Empty as EmptyQueueException

import networkx
from bs4 import BeautifulSoup
# import matplotlib.pyplot as plt


# TODO analyse the web-scraping, find ways to speed it up.
# TODO add argpharsing for CLI usage.


# Argparse:
#       first user url,     degrees of separation,  [first user name]
#       [output file name, write graph data to file.]
#       [output to console]
#       [verbosity (info level logging)
#           low: current degree, number of users processed
#           medium: adding of nodes, edges
#           high: discovery of colleagues, current processing time, estimated remaining time.]
#
#           never shown: debugging logging.

random.seed(-1)

DEBUG = True

# important constants, for web scraping
URL_YOUTUBE_USER = 'https://www.youtube.com'
SUBURL_YOUTUBE_CHANNELS = '/channels?view=60'
RELATED_CHANNELS_TAG = 'li'
RELATED_CHANNEL_TAG_NAME = 'h3'
RELATED_CHANNELS_CLASS_ATTR_VALUE = 'channels-content-item yt-shelf-grid-item'
RELATED_CHANNELS_SUBHREF_ATTR_NAME = 'data-external-id'

# defaults
DEFAULT_FIRST_USER = ('Cryaotic', URL_YOUTUBE_USER + '/channel/UCu2yrDg7wROzElRGoLQH82A' + SUBURL_YOUTUBE_CHANNELS)
DEFAULT_MAX_DEGREES_OF_SEPARATION = 2

# for debugging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)-15s ### %(filename)-15s - %(lineno)-5d ::: %(levelname)-6s - %(message)s')
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
    soup = BeautifulSoup(urllib.urlopen(url), 'html.parser')

    # scrape the tags representing related channels
    channels = soup.find_all(RELATED_CHANNELS_TAG, attrs={'class':RELATED_CHANNELS_CLASS_ATTR_VALUE})

    ret_list = list()

    for channel in channels:
        # channel name is text in form "<name> <delimiter> Channel", we want only <name>.
        element = channel.find(RELATED_CHANNEL_TAG_NAME).a
        user_name = element['title']
        link = URL_YOUTUBE_USER + element['href'] + SUBURL_YOUTUBE_CHANNELS
        listing = (user_name, link)
        ret_list.append(listing)

    return ret_list


def generate_colours():
    color_list = list()
    # get list of all possible colours.
    colors = list()
    # for x colours in scale, there are x^3 colours produced
    scale = range(0,257,(255/(DEFAULT_MAX_DEGREES_OF_SEPARATION/2)))
    if DEBUG:
        logger.debug('color scale: ' + str(scale))
    for i in itertools.product(scale, scale, scale):
        # convert from (R, G, B)decimal to '#RRGGBB'hex
        c = '#' + hex(i[0])[2:].zfill(2) + hex(i[1])[2:].zfill(2) + hex(i[2])[2:].zfill(2)
        colors.append(c)
    # dump existing colours, and black and white
    del colors[0]
    del colors[-1]
    # create list of colours, unique per degree of separation
    for i in range(DEFAULT_MAX_DEGREES_OF_SEPARATION + 2):
        x = random.randint(0, len(colors))
        color_list.append(colors[x])
        if DEBUG:
            logger.debug('new color for degree ### ' + str(i).zfill(2) + ' ::: ' + colors[x])
        del colors[x]

    return color_list


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


def generate_graph():

    logger.info('Generating graph now...')

    graph_nodes.clear()
    if DEBUG:
            logger.debug('graph objects ready.')

    degree = 0
    users_to_do.append(DEFAULT_FIRST_USER)

    while degree < DEFAULT_MAX_DEGREES_OF_SEPARATION:
        while len(users_to_do) > 0:
            user_queue.put(users_to_do.pop())

        while True:

                if DEBUG:
                    logger.debug('processed users - ' + str(len(users_processed)))

                # unload the next level of users from the next_users deque.
                if user_queue.empty() or user_queue.qsize() < 1:
                    # ran out of next_users - stop analyzing this level
                    break
                user_name, url = user_queue.get()

                if user_name in graph_nodes.nodes():
                    if DEBUG:
                        logger.debug('skipping user - ' + user_name)
                    continue
                else:
                    graph_nodes.add_node(user_name, degree=degree)
                    users_processed.append( (user_name, url) )

                    if DEBUG:
                        logger.debug('new graph node - ' + user_name)

                    if DEBUG:
                        logger.debug('user queue size - ' + str(user_queue.qsize()))

                    # list of (name, url) tuples with edge to this user url.
                    associations = get_association_list(url)
                    for colleague in associations:
                        colleague_name, _  = colleague
                        if DEBUG:
                            logger.debug('discovered colleague - ' + colleague_name)
                        if colleague_name in graph_nodes.nodes():
                            graph_nodes.add_edge(user_name, colleague_name)
                            if DEBUG:
                                logger.debug('new edge - ' + user_name + ', ' + colleague_name)
                        elif degree < DEFAULT_MAX_DEGREES_OF_SEPARATION \
                                and colleague not in users_processed \
                                and colleague not in users_to_do:
                            users_to_do.append(colleague)

                    if DEBUG:
                        logger.debug('finished colleague discovery.')

        degree += 1

        if DEBUG:
            logger.debug('new degree: ' + str(degree) + ' #######')

    logger.info ('Graph generation complete.')

    return


def show_graph():
    colors = generate_colours()
    networkx.draw_spring(graph_nodes,
                         node_color=[colors[graph_nodes.node[node]['degree']] for node in graph_nodes])

    return


if __name__=='__main__':
    generate_graph()
    show_graph()