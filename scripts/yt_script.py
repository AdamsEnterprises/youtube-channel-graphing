#!/usr/env python
"""
Main script for tge youtube graphing project.
"""
from __future__ import absolute_import, print_function, nested_scopes, generators, with_statement

from logging import getLogger, StreamHandler, Formatter
from logging import INFO
# from multiprocessing import JoinableQueue as JQueue
try:
    from queue import Queue
    from queue import Empty as EmptyQueueException
except ImportError:
    from Queue import Queue
    from Queue import Empty as EmptyQueueException

import argparse
from itertools import cycle
import json
try:
    from googleapiclient import discovery
    from googleapiclient.errors import HttpError
    import networkx
    from networkx.readwrite import json_graph
except ImportError:
    print ('''ERROR: the networkX and google-api-client modules are required.
    You can install these modules through pip.''')
    exit()



DETAILED_MESSAGE = '%(asctime)-15s >>> %(funcName)s, line:%(lineno)d --- %(message)s'

API_YOUTUBE_SERVICE = 'youtube'
API_VERSION = 'v3'

TEMP_FILENAME = '!__temp__'
DEFAULT_OUTPUT_FILENAME = 'graph.out'

OUTPUT_FORMATS = ['text', 'graphml', 'gml', 'gexf', 'yaml']


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
        logger.setLevel(INFO)
        if not getattr(logger, 'handler_set', None):
            formatter = Formatter(DETAILED_MESSAGE)
            console_handler = StreamHandler()
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
            logger.handler_set = True
    return logger


def declare_degree(logger, degree):
    """
    make logger show the current degree
    :param degree: the degree to show
    :return:
    """
    if logger is not None:
        logger.info('\nDegree: #{}'.format(degree))


def declare_warning(logger, warning):
    """
    log a warning message.
    :param logger: the Logger object for message output.
    :param warning: the message.
    :return:
    """
    if logger is not None:
            logger.warning(warning)


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
                        choices=OUTPUT_FORMATS,
                        help="""Format to convert the graph data into. Valid choices are:
                        text (default) - tab formatted text listing edges and related nodes.
                        graphml - xml formatted according to graphml specifications.
                        """)
    parser.add_argument('-v', '--verbose', action='store', type=int, default=0,
                        choices=[1, 2, 3],
                        help="""Display additional information to the console during processing.
                        The default (if ommitted) is to not display any information.
                        Possible choices are:
                        1 - current degree of separation being processed.
                        2 - Total users processed.
                        3 - New users, and relationships between users, found.""")
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
        """
        check the filename does not have invalid characters.
        :return:
        """
        # arguments is from outer scope
        # check if filename is valid
        for symbol in "\"\\|/?,<>:;'{[}]*&^%":
            if symbol in arguments.filename:
                raise AttributeError(" '-f <filename>': <filename> contains an" +
                                     " invalid symbol: \"\\|/?,<>:;'{[}]*&^%")

    def _assert_valid_degree():
        """
        check the supplied degree is a positive integer.
        :return:
        """
        # arguments is from outer scope
        try:
            deg = int(arguments.degree)
            assert deg > 0
        except (AssertionError, ValueError):
            raise AttributeError(" '-d <degree>': <degree> should be a positive integer.")

    def _assert_valid_channel_id():
        """
        check the channel id is for a real channel.
        :return:
        """
        # arguments is from outer scope
        try:
            # check for malformed urls
            # this is too unreliable to test.
            if arguments.id is None or len(arguments.id) == 0:  # pragma: no cover
                raise AttributeError(" '<id>': Could not verify the channel id. Please check " +
                                     "this id is correct.\nYou may not use a legacy username - " +
                                     "only use a channel id.\nChannel Ids can be found at urls " +
                                     "such as 'https://www.youtube.com/channel/<id>'.")
            temp_api = create_youtube_api(developer_key=arguments.api_key)
            api_channels = temp_api.channels()
            response = api_channels.list(part='snippet', id=arguments.id).execute()
            # check this is the correct kind of response
            # difficult to reliably test
            if not ('kind' in response and 'items' in response and
                    response['kind'] == 'youtube#channelListResponse' and
                    len(response['items']) > 0):    # pragma: no cover
                raise AttributeError(" '<id>': Could not verify the channel id. Please check " +
                                     "this id is correct.\nYou may not use a legacy username - " +
                                     "only use a channel id.\nChannel Ids can be found at urls " +
                                     "such as 'https://www.youtube.com/channel/<id>'.")
        # only occurs with malformed api requests or unusual errors from network or api itself.
        except HttpError as http_excp:  # pragma: no cover
            if "HttpError 400" in str(http_excp):
                raise RuntimeError("""Error in create_youtube_api(key):
                                   is key a valid api_key? is key spelt correctly?""")

    if args is None:
        arguments = parser.parse_args()
    else:
        arguments = parser.parse_args(args)

    _assert_valid_filename()
    _assert_valid_degree()
    _assert_valid_channel_id()

    return arguments


def create_youtube_api(developer_key=None):
    """
    generate an api object for interfacing with the google youtube api.
    :param developer_key: api_key for use by developers
    :return:
    """
    try:
        if developer_key is None:
            raise RuntimeError(" '<api_key>' developerKey cannot be null.")
        api = discovery.build(serviceName=API_YOUTUBE_SERVICE, version=API_VERSION,
                              developerKey=developer_key)
        return api
    except HttpError as http_excp:    # pragma: no cover
        if "HttpError 400" in str(http_excp):
            raise RuntimeError("""Error in create_youtube_api(key):
                               is key a valid api_key? is key spelt correctly?""")


def get_association_list(channel_id, api):
    """
    grab a list of associated channels
    :param channel_id: the id of the channel to collect associations from.
    :param api: the google api object.
    :return: a list of (associated channel name, associated channel id).
    """

    def _create_associate_list():
        """
        make a list of associates through an api brandingSettings request
        :return: list of associate channels
        """

        result = api.channels().list(part='brandingSettings', id=channel_id).execute()
        if len(result['items']) == 0:
            return None
        channels = result['items'][0]['brandingSettings']['channel']['featuredChannelsUrls']
        for channel in channels:
            associate_list.append(channel)

    if channel_id is None or api is None:
        raise RuntimeError("""Error in get_association_list(i, a):
                           'i' or 'a' parameter was None.""")
    try:
        associate_list = list()
        _create_associate_list()
        return associate_list
    except AttributeError as att_excp:
        if 'has no attribute' in str(att_excp):
            raise RuntimeError("""Error in get_association_list(i, a):
                               was expecting 'a' to be a youtube api client.""")
        else:
            raise att_excp
    except HttpError as http_excp:    # pragma: no cover
        if "HttpError 400" in str(http_excp):
            raise RuntimeError("""Error in get_association_list(i, a):
                               failed request to youtube api - check the api_key is correctly
                               spelt.""")
    except KeyError:
        return None


def extract_user_name(channel_id, api):
    """
    get the username for a given channel
    :param channel_id: the id of the channel to collect the user name from.
    :param api: the google api object.
    :return: the user name.
    """

    def _find_title():
        """
        grab the channel title through an api brandingSettings request
        :return: channel title
        """
        result = api.channels().list(part='brandingSettings', id=channel_id).execute()
        if len(result['items']) == 0:
            return None
        return result['items'][0]['brandingSettings']['channel']['title']

    if channel_id is None or api is None:
        raise RuntimeError("""Error in extract_user_name(i, a):
                           'i' or 'a' parameter was None.""")
    try:
        title = _find_title()
        return title
    except AttributeError as att_excp:
        if 'has no attribute' in str(att_excp):
            raise RuntimeError("""Error in extract_user_name(i, a):
                               was expecting 'a' to be a youtube api client.""")
        else:
            raise att_excp
    # unreliable to test
    except HttpError as http_excp:      # pragma: no cover
        if "HttpError 400" in str(http_excp):
            raise RuntimeError("""Error in extract_user_name(i, a):
                               failed request to youtube api - check the api_key is correctly
                               spelt.""")
    except KeyError:
        return None


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
    with open(filename, 'w') as f_handle:
        f_handle.write(json.dumps(data))
    return


def generate_output(graph, output_format, filename):
    """
    Send the graph to console as adjacency list text, or to a file in a specified format.
    :param graph: The networkX graph object
    :param output_format: how to format the output graph data
    :param filename: the file to write to. if output_format is None, then this is ignored.
    :return:
    """

    def _get_output_funcs_list():
        """
        get a sequence of conversion functions.
        :return: list of conversion functions.
        """
        return [convert_graph_to_text, convert_graph_to_graphml, convert_graph_to_gml,
                convert_graph_to_gexf, convert_graph_to_yaml]

    if output_format is None:
        for text in networkx.generate_adjlist(graph):

            print(text)
    elif output_format not in OUTPUT_FORMATS:
        raise RuntimeError("""Error in generate_output(g, o, f): 'o' has an unrecognised value.
                           value of 'o'=""" + output_format)
    else:
        # temporary mapping of format codes to formatter funcs.
        output_funcs = _get_output_funcs_list()
        output_mapping = dict()
        for index in range(len(OUTPUT_FORMATS)):
            try:
                output_mapping[OUTPUT_FORMATS[index]] = output_funcs[index]
            # do not test: exists as catch
            except IndexError:      # pragma: no cover
                break
        # now convert to the format and write to file.
        output_mapping[output_format](graph, filename)
    return


def build_graph(graph, api, max_depth=1, initial_channel=None, logger=None):
    """
    given an initial graph and node, build a complete tree graph out to a given depth.
    :param graph: the networkx graph object to work with.
    :param max_depth: furthermost depth to build to, e.g. 1 gets immediate associates,
        2 gets associates of immediate associates, etc.
    :param initial_channel: the channel id for the initial node
    :param logger: logging object for generating verbose messages
    :return:
    """
    if initial_channel is None:
        return

    def _transfer_next_ids_to_queue():
        """
        queue the next se of ids to process.
        :return:
        """
        while len(next_channel_ids) > 0:
            channel_id = next_channel_ids.pop()
            if channel_id not in processed_ids:
                id_queue.put(channel_id)
        return

    def _process_associates():
        """
        get the list of associates, produce graph nodes and edges, and prep for future processing.
        :return:
        """
        associates = get_association_list(current_id, api)
        if associates is None:
            declare_warning(logger, """Could not retrieve this channel's associates. This
                            information may be unavailable at this time.
                            channel id = """ + current_id)
        else:
            for index in range(len(associates)):
                assoc_id = associates[index]
                assoc_name = extract_user_name(assoc_id, api)
                if assoc_name is not None:
                    if assoc_name not in graph.nodes():
                        graph.add_node(assoc_name, degree=depth)
                        declare_new_node(logger, assoc_name)
                    if (current_name, assoc_name) not in graph.edges() and \
                            (assoc_name, current_name) not in graph.edges():
                        graph.add_edge(current_name, assoc_name)
                        declare_new_edge(logger, current_name, assoc_name)
                    if assoc_id not in next_channel_ids:
                        next_channel_ids.append((assoc_name, assoc_id))
                else:
                    declare_warning(logger, """Could not retrieve this channel's name. This
                                    information may be unavailable at this time.
                                    channel id = """ + assoc_id)

    id_queue = Queue()
    processed_ids = set()
    next_channel_ids = list()
    current_name = extract_user_name(initial_channel, api)
    if current_name is None:
        raise RuntimeError("""Could not retrieve the initial channel's name. The channel may not
                           have the required information set to public.""")
    graph.add_node(current_name, degree=0)
    id_queue.put((current_name, initial_channel))
    depth = 1
    while depth <= max_depth:
        declare_degree(logger, depth)
        while id_queue.qsize() > 0 and not id_queue.empty():
            current_name, current_id, = id_queue.get()
            _process_associates()
            processed_ids.add(current_id)
            declare_processed_users(logger, len(processed_ids))
            # id_queue.task_done()
        _transfer_next_ids_to_queue()
        depth += 1
    while not id_queue.empty():
        try:
            id_queue.get(timeout=0.001)
        except EmptyQueueException:
            continue
    # id_queue.close()
    return


def build_colour_generator():
    """
    create a generator for assigning colours.
    :return: generator, for colours.
    """
    yield '#ffffff'
    colour_list = cycle(['#ffff22', '#ff44ff', '#22ffff'])
    while True:
        yield next(colour_list)


def main_function():
    """
    the runner function of the main_script
    :return:
    """
    try:
        parser = setup_arg_parser()
        arguments = verify_arguments(parser, None)
        logger = prepare_logger(arguments.verbose)
        api = create_youtube_api(developer_key=arguments.api_key)
        # colour generator

        youtube_user_graph = networkx.Graph()
        youtube_user_graph.clear()
        build_graph(youtube_user_graph, api, max_depth=arguments.degree,
                    initial_channel=arguments.id, logger=logger)
        generate_output(youtube_user_graph, arguments.output, arguments.filename)
        # causes issues due to matplotlib use.
        if arguments.show_graph:            # pragma: no cover
            colours = build_colour_generator()
            colours_dict = dict()
            for i in range(arguments.degree + 1):
                colours_dict[i] = next(colours)
            import matplotlib.pyplot as plt
            # labels=networkx.draw_networkx_labels(
            #     youtube_user_graph,pos=networkx.spring_layout(youtube_user_graph))
            networkx.draw_networkx(youtube_user_graph, with_labels=True,
                                   node_color=[colours_dict[youtube_user_graph.node[node]['degree']]
                                               for node in youtube_user_graph])
            plt.show()
    except (AttributeError, HttpError) as excp:
        print('ERROR: ' + str(excp))

if __name__ == '__main__':
    main_function()
