__author__ = 'Roland'

import argparse

def setup_arg_parser():
    """
    prepare and set up the argumentParser for this script
    :return: the argumentParser
    """

    # TODO: add options for different output data formats

    parser = argparse.ArgumentParser(description="""Collect and/or show graphing data upon a
                                                 Youtube user and their relationships to other
                                                 users.""")
    parser.add_argument('id', action='store', type=str,
                        help="ID of the channel of the initial user.")
    parser.add_argument('api_key', action='store', type=str,
                        help="The api_key required to access the Youtube API.")
    parser.add_argument('-d', '--degree', action='store', type=int, default=1,
                        help="The degree of separation to process to. Must be an integer" +
                             " greater than 0. Default is 1.")
    parser.add_argument('-f', '--filename', action='store', type=str,
                        help="""A file to record graphing data to. Must be a valid name for the
                        operating system. If the option is omitted then no file is made.""")
    parser.add_argument('-o', '--output', action='store', type=str, default='text',
                        choices=['text', 'graphml', 'gml','gexf','json','yaml'],
                        help="""Format to convert the graph data into. Valid choices are:
                        text (default) - tab formatted text listing edges and related nodes.
                        graphml - xml formatted according to graphml specifications.
                        gexf -
                        gml -
                        json -
                        yaml -
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


if __name__=='__main__':
    parser = setup_arg_parser()
    print (parser.parse_args(['1','2']))
