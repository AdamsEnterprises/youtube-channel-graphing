"""
Main script for tge youtube graphing project.
"""
from __future__ import absolute_import, print_function, nested_scopes, generators, with_statement

__author__ = 'Roland'

# TODO: change output arguments, if no output argument then no record to file and show only adjacency list to console, otherwise write formatted output to file.

from logging import getLogger, StreamHandler, Formatter
from logging import ERROR, INFO

import itertools
import random
import multiprocessing
#  from Queue import Empty as EmptyQueueException
import argparse
import json

from googleapiclient import discovery
from googleapiclient.errors import HttpError


import networkx
from networkx.readwrite import json_graph
import matplotlib.pyplot as plt

random.seed(-1)


GENERAL_MESSAGE = '%(message)s'
DETAILED_MESSAGE = '%(asctime)-15s --- %(levelname)-6s : %(message)s'

API_YOUTUBE_SERVICE = 'youtube'
API_VERSION = 'v3'

TEMP_FILENAME = '!__temp__'
DEFAULT_OUTPUT_FILENAME = 'graph.out'

def prepare_logger(verbosity):
    """
    setup the logger
    :param verbosity: determines how much information the logger is to show
    :return:
    """
    if verbosity == 0:
        return None
    else:
        logger = getLogger('youtube_user_graph')
        logger.verbosity = verbosity
        if verbosity == 1:
            logger.setLevel(ERROR)
            formatter = Formatter(GENERAL_MESSAGE)
        else:
            logger.setLevel(INFO)
            if verbosity >= 4:
                formatter = Formatter(DETAILED_MESSAGE)
            else:
                formatter = Formatter(GENERAL_MESSAGE)
        console_handler = StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    return logger


def declare_error(logger, message):
    """
    makes the logger show an error message
    :param message: the error message to show
    :return:
    """
    if logger is not None:
        logger.error(message)


def declare_degree(logger, degree):
    """
    make logger show the current degree
    :param degree: the degree to show
    :return:
    """
    if logger is not None:
        if logger.verbosity >= 2:
            logger.info('Degree: #{}'.format(degree))


def declare_processed_users(logger, user_count):
    """
    make logger show the number of processed users
    :param user_count: how many users have been processed.
    :return:
    """
    if logger is not None:
        if logger.verbosity >= 2:
            logger.info('Users Processed: {}'.format(user_count))


def declare_new_node(logger, node):
    """
    make logger show that a new node has been added
    :param node: the new node
    :return:
    """
    if logger is not None:
        if logger.verbosity >= 3:
            logger.info('New Node: {}'.format(node))


def declare_new_edge(logger, edge_start, edge_end):
    """
    make logger show that a new edge has been added
    :param edge_start: the first node in the edge
    :param edge_end: the last node in the edge
    :return:
    """
    if logger is not None:
        if logger.verbosity >= 3:
            logger.info('New Edge: {} to {}'.format(edge_start, edge_end))


def setup_arg_parser():
    """
    prepare and set up the argumentParser for this script
    :return: the argumentParser
    """
    parser = argparse.ArgumentParser(description="""Collect and/or show graphing data upon a
                                                 Youtube user and their relationships to other
                                                 users.""")
    parser.add_argument('id', action='store', type=str,
                        help="A youtube channel id. The referenced channel is treated as the" +
                        " initial user.")
    parser.add_argument('api_key', action='store', type=str,
                        help="The api key with which to access the youtube API.")
    parser.add_argument('-d', '--degree', action='store', type=int, default=1,
                        help="The degree of separation to process to. Must be an integer" +
                             " greater than 0. Default is 1.")
    parser.add_argument('-f', '--filename', action='store', type=str,
                        default=DEFAULT_OUTPUT_FILENAME,
                        help="""A file to record graphing data to. Must be a valid name for the
                        operating system. If the option is omitted then no file is made.""")
    parser.add_argument('-o', '--output', action='store', type=str, default=None,
                        choices=['text', 'graphml', 'gml','gexf','json','yaml'],
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
        # arguments is from outer scope
        try:
            # check if filename is valid
            if arguments.filename is not None:
                for symbol in "\"\\|/?,<>:;'{[}]*&^%":
                    assert symbol not in arguments.filename
        except AssertionError:
            raise AttributeError("filename contains invalid symbols: \"\\|/?,<>:;'{[}]*&^%")

    def _assert_valid_degree():
        # arguments is from outer scope
        try:
            deg = int(arguments.degree)
            assert deg > 0
        except (AssertionError, ValueError):
            raise AttributeError("Degree should be a positive integer.")

    def _assert_valid_channel_id():
        # arguments is from outer scope
        try:
            # check for malformed urls
            assert arguments.id is not None
            assert len(arguments.id) > 0
            temp_api = create_youtube_api(developerKey=arguments.api_key)
            response = temp_api.channels().list(part='snippet', id=arguments.id).execute()
            # check this is the correct kind of response
            assert 'kind' in response
            assert response['kind'] == 'youtube#channelListResponse'
            # check the response is from a real channel
            assert 'items' in response
            assert len(response['items']) > 0
        except AssertionError:
            raise AttributeError("Could not verify the channel id. Please check this id is correct.")

    if args is None:
        arguments = parser.parse_args()
    else:
        arguments = parser.parse_args(args)

    _assert_valid_filename()
    _assert_valid_degree()
    _assert_valid_channel_id()

    return arguments


def create_youtube_api(developerKey=None):
    """
    generate an api object for interfacing with the google youtube api.
    :param developerKey:
    :return:
    """
    if developerKey is None:
        raise HttpError('Error: developerKey cannot be null.')
    api = discovery.build(serviceName=API_YOUTUBE_SERVICE, version=API_VERSION,
                          developerKey=developerKey)
    return api



def get_association_list(id, api):
    """
    grab a list of associated channels
    :param id: the id of the channel to collect associations from.
    :param api: the google api object.
    :return: a list of (associated channel name, associated channel id).
    """

    if id is None or api is None:
        raise AttributeError('id must be a channel id and api must be a googleapi object.')
    try:
        result = api.channels().list(part='brandingSettings', id=id).execute()
        if len(result['items']) == 0:
            raise AttributeError('No channel information found. Please check the channel id '+
                                'is correct\nchannel id=' + str(id))
        associate_list = list()
        channels = result['items'][0]['brandingSettings']['channel']['featuredChannelsUrls']
        for channel in channels:
            associate_list.append( (extract_user_name(channel, api), channel) )
        return associate_list

    except AttributeError as a:
        if 'has no attribute' in a.message:
            raise AttributeError('api must be a google api object. Please check the correct' +
                                 ' object was supplied.')
        else:
            raise a


def extract_user_name(id, api):
    """
    get the username for a given channel
    :param id: the id of the channel to collect the user name from.
    :param api: the google api object.
    :return: the user name.
    """
    if id is None or api is None:
        raise AttributeError('id must be a channel id and api must be a googleapi object.')
    try:
        result = api.channels().list(part='brandingSettings', id=id).execute()
        if len(result['items']) == 0:
            raise AttributeError('No channel information found. Please check the channel id '+
                                'is correct\nchannel id=' + str(id))
        title = result['items'][0]['brandingSettings']['channel']['title']
        return title
    except AttributeError as a:
        if 'has no attribute' in a.message:
            raise AttributeError('api must be a google api object. Please check the correct' +
                                 ' object was supplied.')
        else:
            raise a


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


def generate_relationship_graph(graph_nodes, max_degree, first_user, logger):
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

    def _process_colleague(origin, current_user, current_degree, user_graph, logger):
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
            declare_new_node(logger, current_user)
        if not user_graph.has_edge(origin, current_user) or \
                user_graph.has_edge(current_user, origin):
            user_graph.add_edge(origin, current_user)
            declare_new_edge(logger, origin, current_user)
        return

    # pylint: disable=maybe-no-member
    user_queue = multiprocessing.Queue()
    users_processed = list()
    users_to_do = list()
    users_to_do.append(first_user)
    degree = 1

    while degree <= max_degree:
        declare_degree(logger, degree)

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
                _process_colleague(user_name, colleague_name, degree, graph_nodes, logger)
                if degree < max_degree \
                        and colleague not in users_processed \
                        and colleague not in users_to_do:
                    users_to_do.append(colleague)

            users_processed.append((user_name, url))
            declare_processed_users(logger, len(users_processed))

        degree += 1
    return graph_nodes


def convert_graph_to_text(graph, filename):
    """
    given a graph object, write a file containing the adjacency list.
    this is the minimum data required to reconstruct the graph.
    :param graph: the graph object to get the list from.
    :param filename: the name of the file to write to.
    :return:
    """
    networkx.write_adjlist(graph, filename)
    return


def convert_graph_to_graphml(graph, filename):
    """
    convert from a networkX graph object, to graphml format.
    :param graph: the networkX graph object.
    :param filename: the name of the file to write to.
    :return:
    """
    networkx.write_graphml(graph, filename, prettyprint=True)
    return


def convert_graph_to_gml(graph, filename):
    """
    convert from a networkX graph object, to gml format.
    :param graph: the networkX graph object.
    :param filename: the name of the file to write to.
    :return:
    """
    networkx.write_gml(graph, filename)
    return


def convert_graph_to_gexf(graph, filename):
    """
    convert from a networkX graph object, to gefx format.
    :param graph: the networkX graph object.
    :param filename: the name of the file to write to.
    :return:
    """
    networkx.write_gexf(graph, filename)
    return


def convert_graph_to_yaml(graph, filename):
    """
    convert from a networkX graph object, to yaml format.
    :param graph: the networkX graph object.
    :param filename: the name of the file to write to.
    :return:
    """
    networkx.write_yaml(graph, filename)
    return


def convert_graph_to_json(graph, filename):
    """
    convert from a networkX graph object, to serialized json format.
    :param graph: the networkX graph object.
    :param filename: the name of the file to write to.
    :return:
    """
    networkx.write_gml(graph, filename)
    # find the lowest degree node
    # store [node_name, degree] and compare for the lowest degree
    root_node = [graph.nodes()[0], graph.node[graph.nodes()[0]]['degree']]
    for node in graph.nodes():
        if graph.node[node]['degree'] < root_node[1]:
            root_node = [node, graph.node[node]['degree']]
            break
    data = json_graph.tree_data(graph, root=root_node[0])
    with open(filename, 'w') as f:
        f.write(json.dumps(data))
    return


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
    logger = prepare_logger(arguments.verbose)
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
