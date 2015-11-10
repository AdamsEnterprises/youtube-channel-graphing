"""
Main script for tge youtube graphing project.
"""
from __future__ import absolute_import, print_function, nested_scopes, generators, with_statement

__author__ = 'Roland'



import urllib as urlManager

try:
    # pylint: disable=no-member
    urlManager.urlopen
except AttributeError:
    #pylint: disable=no-member
    from urllib import request as urlManager


from logging import getLogger, StreamHandler, Formatter
from logging import ERROR, INFO

import itertools
import random
import multiprocessing
#  from Queue import Empty as EmptyQueueException
import argparse

import networkx
import bs4
import matplotlib.pyplot as plt

random.seed(-1)

# TODO: switch from web scraping to Youtube API

# url      <url to featured channel list>
#           test:   url actually leads to valid featured channel webpage
#           test:   url is no null
#
# [-d --degrees]    <degrees of separation>
#           ( if not specified, assume 1 degree.)
#           test: degrees is not null
#           test: degrees is an integer greater than 0.
# [-f -filename]    <file to write output graph data into>
#           test:   filename is not null
#           test:   filename is valid for underlying system.
#           test:   produced file is not empty
#           test:   produced file has expected nodes and edges
# [-v --verbosity]  <display info logging to console>
#                   (default - 0: off)
#                   (0: off)
#                   (1: warnings, errors only)
#                   (2: current degree and number of users processed...)
#                   (3: new nodes, new edges)
#                   (4: date and time of message)
#           test:   verbosity level gives correct format response
#           (need to capture logging messages for comparison)
# [-s --show_graph]
#                   show a visual depiction of the resultant graph.
# [-h --help]   <help information on options>
#           test: expected output produced.


# important constants, for web scraping
URL_YOUTUBE_CHANNEL_ROOT = u'https://www.youtube.com'
SUBURL_YOUTUBE_USER = u'/user'
SUBURL_YOUTUBE_CHANNELS = u'/channels'
SUBURL_CHANNEL_PARAMS = u'?view=60'
RELATED_CHANNEL_INDIVIDUAL_TAG = 'li'
RELATED_CHANNEL_CLASS_ATTR_VALUE = 'channels-content-item yt-shelf-grid-item'
RELATED_CHANNEL_SUBTAG = 'h3'
RELATED_CHANNELS_ANCHOR_ID = 'c4-primary-header-contents'
RELATED_CHANNELS_ANCHOR_SOURCE = 'a'
RELATED_CHANNELS_ROOT_TAG = 'ul'
RELATED_CHANNELS_ROOT_ID_VALUE = 'browse-items-primary'

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


def setup_arg_parser():
    """
    prepare and set up the argumentParser for this script
    :return: the argumentParser
    """

    # TODO: add options for different output data formats

    parser = argparse.ArgumentParser(description="""Collect and/or show graphing data upon a
                                                 Youtube user and their relationships to other
                                                 users.""")
    parser.add_argument('url', action='store', type=str,
                        help="A url to a listing of featured channels. This is treated" +
                             " as the initial Youtube user.")
    parser.add_argument('-d', '--degree', action='store', type=int, default=1,
                        help="The degree of separation to process to. Must be an integer" +
                             " greater than 0. Default is 1.")
    parser.add_argument('-f', '--filename', action='store', type=str,
                        help="""A file to record graphing data to. Must be a valid name for the
                        operating system. If the option is omitted then no file is made.""")
    parser.add_argument('-o', '--output', action='store', type=str, default='text',
                        choices=['text', 'graphml'],
                        help="""Format to convert the graph data into. Valid choices are:
                        text (default) - tab formatted text listing edges and related nodes.
                        graphml - xml formatted according to graphml specifications.
                        """)
    parser.add_argument('-v', '--verbose', action='store', type=int, default=0,
                        choices=[1, 2, 3, 4],
                help="""Display additional information to the console during processing.
                     The default (if ommitted) is to not display any information.
                     Possible choices are:
                     1 - Non-critical Errors and warnings.
                     2 - Total users processed, the current degree of separation being processed.
                     3 - New users, and relationships between users, found.
                     4 - Fully formatted logging with date and time. Useful for bug reports.""")
    parser.add_argument('-s', '--show_graph', action='store_true', default=False,
                        help="Display a visual depiction of the graph in a separate window, "
                        + "when processing is complete.")
    return parser


def verify_arguments(parser, args):
    """
    Parse a sequence of arguments, given an argumentParser and a list of arguments.
    :param parser:  the argumentParser to use.
    :param args:    list of arguments to process
    :return:        the parsed Arguments object.
    """

    def _assert_valid_filename():
        try:
            # check if filename is valid
            if arguments.filename is not None:
                for symbol in "\"\\|/?,<>:;'{[}]*&^%":
                    assert symbol not in arguments.filename
        except AssertionError:
            raise ValueError("""filename contains invalid symbols. Please
                             see the help section for more information.""")

    def _assert_valid_channel_url():
        # check correct youtube url for featured channels
        assert ('/' + url.split('/')[-1]) == str(SUBURL_YOUTUBE_CHANNELS)
        temp = url.rsplit('/', 2)[0]
        # expecting origin url in user format.
        assert temp == str(URL_YOUTUBE_CHANNEL_ROOT + SUBURL_YOUTUBE_USER)
        # don't check params - just replace them with the correct ones, which we already know
        if ('?' + params) != SUBURL_CHANNEL_PARAMS:
            arguments.url = url + SUBURL_CHANNEL_PARAMS
        # fully check that this url actually works
        name = extract_first_user_name(arguments.url)
        # should raise ValueError if cannot parse associates.
        get_association_list(arguments.url)
        if len(name) == 0:
            raise AssertionError

    if args is None:
        arguments = parser.parse_args()
    else:
        arguments = parser.parse_args(args)

    _assert_valid_filename()

    try:
        # check for malformed urls
        assert arguments.url is not None
        assert len(arguments.url) > 0
        try:
            url, params = arguments.url.split('?')
        except ValueError:
            url = arguments.url
            params = ''
        _assert_valid_channel_url()
    except AssertionError:
        raise ValueError("the URL supplied is not a valid youtube featured channels url.")

    return arguments


def get_association_list(url):
    """
    grab the webpage at the given url
    :param url: the url to retrieve associated channels from.
    :return: a list of (user name, associated channel url).
    """

    strainer = bs4.SoupStrainer(RELATED_CHANNELS_ROOT_TAG,
                                attrs={'id': RELATED_CHANNELS_ROOT_ID_VALUE})

    # scrape the tags representing related channels
    channel_root = bs4.BeautifulSoup(urlManager.urlopen(url), 'html.parser', parse_only=strainer)

    if len(channel_root) == 0:
        raise ValueError("""cannot parse or locate root element of related channels.
                         Check the url is actually for a featured channels page. """)

    ret_list = list()

    channels = channel_root.find_all(RELATED_CHANNEL_INDIVIDUAL_TAG,
                                     attrs={'class': RELATED_CHANNEL_CLASS_ATTR_VALUE})

    for channel in channels:
        if not isinstance(channel, bs4.Tag):
            continue
        # channel name is text in form "<name> <delimiter> Channel", we want only <name>.
        try:
            element = channel.find(RELATED_CHANNEL_SUBTAG)
            element_anchor = element.a
            user_name = element_anchor['title']
            link = URL_YOUTUBE_CHANNEL_ROOT + element_anchor['href'] + \
                SUBURL_YOUTUBE_CHANNELS + SUBURL_CHANNEL_PARAMS
        except (KeyError, AttributeError):
            logger.declare_error('Could not parse HTML element on this page, ' +
                                'may be malformed: ' + str(url))
            continue
        listing = (user_name, link)
        ret_list.append(listing)

    return ret_list


def extract_first_user_name(url):
    """
    grab the source user name at the given url
    :param url: the url to retrieve source user name from.
    :return: string, the source user name.
    """
    strainer = bs4.SoupStrainer(attrs={'id': RELATED_CHANNELS_ANCHOR_ID})
    # scrape the tag with the user name
    name_tag = bs4.BeautifulSoup(urlManager.urlopen(url), 'html.parser', parse_only=strainer)
    return name_tag.find(RELATED_CHANNELS_ANCHOR_SOURCE)['title']


def generate_colours(value):
    """
    create a list of random colours.
    :param value: an integer influencing how many colours to create
    :return: a list of (value + 1) colours
    """

    def create_colour_code_permutations(value_range):
        """
        # create a list of all colour code permutations, depending on a given range of values.
        :return: list of colour codes
        """
        permutation_list = list()
        for i in itertools.product(value_range, value_range, value_range):
            # convert from (R, G, B)decimal to '#RRGGBB'hex
            code = '#' + hex(i[0])[2:].zfill(2) + hex(i[1])[2:].zfill(2) + hex(i[2])[2:].zfill(2)
            permutation_list.append(code)
        return permutation_list

    if not isinstance(value, int):
        raise TypeError("Parameter must be Integer.")
    if value <= 0:
        raise ValueError("Parameter must be greater than or equal to 1.")
    color_list = list()
    # for x colours required, there are x^3-2 colours produced
    factor = 2
    # rnumber of degrees is (0, ..., n) thus number of colours returned = n + 1
    while value + 1 > ((factor * factor * factor) - 2):
        factor += 1
    scale_factor = int((256.0 / (factor - 1) - 0.1))
    scale = range(0, 256, scale_factor)
    code_list = create_colour_code_permutations(scale)
    # dump existing colours, and black and white
    del code_list[0]
    del code_list[-1]
    # create list of colours, unique per degree of separation

    while value >= 0:
        index = random.randint(0, len(code_list) - 1)
        color_list.append(code_list[index])
        del code_list[index]
        value -= 1

    return color_list


def generate_relationship_graph(graph_nodes, max_degree, first_user, verbosity):
    """
    creates a graphing object representing you tube users and associations.
    :param graph_nodes: the object storing the graph nodes and edges.
        must conform to networkx.Graph object API.
    :return: a networkX graph object, containg users as nodes and relationships as edges.
    """

    def _queue_next_users__to_do(user_list, queue):
        """
        transfer list of next users into the queue
        :param user_list:   list of next users
        :param queue:       queue to transfer to
        :return:
        """
        while len(users_to_do) > 0:
            user = user_list.pop()
            queue.put(user)
        return

    def _process_colleague(origin, current_user, current_degree, user_graph, verbosity):
        """
        add a colleague to the nodes and edges as needed. enlist the colleague if not already
        processed.
        :param origin:          user this colleague relates to
        :param current_user:    the colleague
        :param user_graph:      the graph to add nodes and edges to.
        :return:
        """
        if not user_graph.has_node(current_user):
            user_graph.add_node(current_user, degree=current_degree)
            logger.declare_new_node(current_user)
        if not user_graph.has_edge(origin, current_user) or \
                user_graph.has_edge(current_user, origin):
            user_graph.add_edge(origin, current_user)
            logger.declare_new_edge(origin, current_user)
        return

    # pylint: disable=maybe-no-member
    user_queue = multiprocessing.Queue()
    users_processed = list()
    users_to_do = list()
    users_to_do.append(first_user)
    degree = 1

    while degree <= max_degree:
        logger.declare_degree(degree)

        _queue_next_users__to_do(users_to_do, user_queue)

        while True:

            # unload the next users from the queue.
            if user_queue.empty() and user_queue.qsize() < 1:
                # ran out of next_users - stop analyzing this level
                break

            user_name, url = user_queue.get()
            # list of (name, url) tuples with edge to this user url.
            associations = get_association_list(url)
            for colleague in associations:
                colleague_name, _ = colleague
                _process_colleague(user_name, colleague_name, degree, graph_nodes, verbosity)
                if degree < max_degree \
                        and colleague not in users_processed \
                        and colleague not in users_to_do:
                    users_to_do.append(colleague)

            users_processed.append((user_name, url))
            logger.declare_processed_users(len(users_processed))

        degree += 1
    return graph_nodes


def convert_graph_to_text(graph):
    """
    given a graph object, render to text the edges in the graph
    this is the minimum data required to reconstruct the graph.
    :param graph: the graph object to get edges from
    :return: a list of edges
    """
    text = ""
    for edge in graph.edges():
        string = str(edge).split("'")[1:-1]
        text += string[0] + ', ' + string[2] + '\n'
    return text


def convert_graph_to_xml(graph):
    """
    convert from a networkX graph object, to a graphml formatted xml string.
    :param graph: the networkX graph object
    :return: the xml describing the graph, in graphml format.
    """
    tree = graphml.make_base_xml()
    for node in graph.nodes():
        graphml.make_node(tree, node, **graph.node[node])
    for edge in graph.edges():
        graphml.make_edge(tree, edge[0], edge[1], **graph.edge[edge[0]][edge[1]])
    return graphml.build_xml_string(tree)


# def convert_graph_to_text(graph):


def generate_file(filename, text):
    with open(filename, 'w') as f:
        f.write(text)


def main_function():
    """
    the runner function of the main_script
    :return:
    """

    parser = setup_arg_parser()
    arguments = verify_arguments(parser, None)
    logger.prepare_logger(arguments.verbose)
    first_user = (extract_first_user_name(arguments.url), arguments.url)
    max_degree = arguments.degree

    youtube_user_graph = networkx.Graph()
    youtube_user_graph.clear()

    youtube_user_graph.add_node(first_user[0], degree=0)
    generate_relationship_graph(youtube_user_graph, max_degree, first_user, 0)

    output = convert_graph_to_text(youtube_user_graph)
    if arguments.output == 'text':
        output = convert_graph_to_text(youtube_user_graph)
    elif arguments.output == 'xml':
        output = convert_graph_to_xml(youtube_user_graph)

    if arguments.filename is not None:
        generate_file(arguments.filename, output)
    else:
        print ("Graph output:\n")
        print (output)

    if arguments.show_graph:
        colors = generate_colours(max_degree)
        networkx.draw_spring(youtube_user_graph,
                             node_color=[colors[youtube_user_graph.node[node]['degree']]
                                         for node in youtube_user_graph])
        plt.show()

if __name__ == '__main__':
    main_function()
