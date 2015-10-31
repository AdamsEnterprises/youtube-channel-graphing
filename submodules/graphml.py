"""
A wrapper module for parsing between graph structures and GraphML format.
"""
from __future__ import absolute_import, print_function, nested_scopes, generators, with_statement

import xml.etree.cElementTree as ET
from xml.dom import minidom

XSI = 'xsi'
SCHEMA_LOCATION = 'schemaLocation'
GRAPHML_TAG = 'graphml'
GRAPH_TAG = "graph"
NODE_TAG = 'node'
EDGE_TAG = 'edge'
EDGE_SOURCE = "source"
EDGE_DEST = "target"
NODE_ID = "id"


def make_base_xml():
    """
    generate the root and graph elements used by GraphML
    :return: root and graph elements, in that order
    """
    ROOT_ELEMENT = ET.Element(GRAPHML_TAG)
    ROOT_ELEMENT.set("xmlns", "http://graphml.graphdrawing.org/xmlns")
    ROOT_ELEMENT.set("xmlns" + ":" + XSI, "http://www.w3.org/2001/XMLSchema-instance")
    ROOT_ELEMENT.set(XSI + ":" + SCHEMA_LOCATION, "http://graphml.graphdrawing.org/xmlns\n" +
                     "http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd")
    GRAPH_ELEMENT = ET.SubElement(ROOT_ELEMENT, GRAPH_TAG)
    GRAPH_ELEMENT.set("id", __name__)
    GRAPH_ELEMENT.set("edgedefault", "undirected")
    tree = ET.ElementTree(ROOT_ELEMENT)
    return tree


def make_node(element_tree, name, **attrs):
    """
    generate a node element, given a graph element to attach to.
    :param graph_element: the xml element representing the graph
    :param name: name of the node
    :param attrs: attributes to attach to the node, as key -> value pairs
    :return: the node xml element
    """
    graph_element = element_tree.find("./" + GRAPH_TAG)
    if graph_element is None:
        raise AttributeError("root element must have an immediate child tagged 'graph'.")
    node = ET.SubElement(graph_element, 'node')
    node.set(NODE_ID, name)
    for attr in attrs:
        node.set(attr, str(attrs[attr]))
    return node


def remove_node_and_linked_edges(element_tree, name):
    """
    given an element tree, remove the first node with an id matching the given name.
    removal of nodes requires the removal of edges associated with the node.
    :param element_tree: the xml element representing the graph.
    :param name: name of the node.
    :return:
    """
    graph_element = element_tree.find("./" + GRAPH_TAG)
    if graph_element is None:
        raise AttributeError("root element must have an immediate child tagged 'graph'.")
    iter = graph_element.iterfind('node')
    for sub_element in iter:
        if sub_element.get(NODE_ID) == name:
            graph_element.remove(sub_element)
            break
    iter = graph_element.iterfind('edge')
    for sub_element in iter:
        if sub_element.get(EDGE_SOURCE) == name or \
                sub_element.get(EDGE_DEST) == name:
            graph_element.remove(sub_element)


def remove_all_nodes_and_edges(element_tree):
    """
    given an element tree, remove all nodes and edges.
    :param element_tree: the xml element representing the graph.
    :return:
    """
    graph_element = element_tree.find("./" + GRAPH_TAG)
    if graph_element is None:
        raise AttributeError("root element must have an immediate child tagged 'graph'.")
    iter = graph_element.iterfind('node')
    for sub_element in iter:
        graph_element.remove(sub_element)
    iter = graph_element.iterfind('edge')
    for sub_element in iter:
        graph_element.remove(sub_element)


def make_edge(element_tree, source, dest, **attrs):
    """
    generate an edge element, given a graph element to attach to.
    :param graph_element: the xml element representing the graph.
    :param source: first node of the edge.
    :param dest: second node of the edge.
    :param attrs: attributes to attach to the edge, as key -> value pairs.
    :return: the node xml element.
    """
    graph_element = element_tree.find("./" + GRAPH_TAG)
    if graph_element is None:
        raise AttributeError("root element must have an immediate child tagged 'graph'.")
    edge = ET.SubElement(graph_element, 'edge')
    edge.set(EDGE_SOURCE, source)
    edge.set(EDGE_DEST, dest)
    for attr in attrs:
        edge.set(attr, str(attrs[attr]))
    return edge


def remove_edge(element_tree, source, dest):
    """
    given an element tree, remove the first edge with a matching source and destination.
    :param element_tree: the xml element representing the graph.
    :param source: name of the first node.
    :param dest: name of the second node.
    :return:
    """
    graph_element = element_tree.find("./" + GRAPH_TAG)
    if graph_element is None:
        raise AttributeError("root element must have an immediate child tagged 'graph'.")
    iter = graph_element.iterfind('edge')
    for sub_element in iter:
        if sub_element.get(EDGE_SOURCE) == source and \
                sub_element.get(EDGE_DEST) == dest:
            graph_element.remove(sub_element)
            break


def remove_all_edges(element_tree):
    """
    given an element tree, remove all edges.
    :param element_tree: the xml element representing the graph.
    :return:
    """
    graph_element = element_tree.find("./" + GRAPH_TAG)
    if graph_element is None:
        raise AttributeError("root element must have an immediate child tagged 'graph'.")
    iter = graph_element.iterfind('edge')
    for sub_element in iter:
        graph_element.remove(sub_element)


def build_xml_string(xml_tree):
    """
    given the root of an xml tree, convert the xml to a formatted string
    :param xml_root: xml root element to parse from
    :return: a prettified string containing formatted xml
    """
    root = xml_tree.getroot()
    xml_string = ET.tostring(root, 'utf-8')
    xml_string = '<?xml version="1.0" ?>\n' + xml_string.decode('utf-8')
    reparsed_string = minidom.parseString(xml_string)
    return reparsed_string.toprettyxml(indent="\t")


def parse_xml_to_element_tree(xml_string):
    """
    given a string containing xml, try to parse it into a graphml tree.
    requires well formed xml, formatted according to graphml standards.
    :param xml_string: string expected to contain xml.
    :return: xml.eTree.cElementTree.ElementTree object containing the graphml data.
    """
    pass
    # verify the xml string
    # parse it into a tree
    # return tree

