"""
A wrapper module for parsing between graph structures and GraphML format.
"""
from __future__ import absolute_import, print_function, nested_scopes, generators, with_statement

import xml.etree.cElementTree as ET
from xml.dom import minidom
import re

XSI = 'xsi'
SCHEMA_LOCATION = 'schemaLocation'
GRAPHML_TAG = 'graphml'
GRAPH_TAG = "graph"
NODE_TAG = 'node'
EDGE_TAG = 'edge'
EDGE_SOURCE = "source"
EDGE_DEST = "target"
ATTR_ID = "id"
ATTR_DIR = "edgedefault"


def make_base_xml(name=__name__, directed=False):
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
    GRAPH_ELEMENT.set(ATTR_ID, name)
    if directed:
        GRAPH_ELEMENT.set(ATTR_DIR, "directed")
    else:
        GRAPH_ELEMENT.set(ATTR_DIR, "undirected")
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
    if name is None:
        raise AttributeError("node parameter cannot be None.")
    node = ET.SubElement(graph_element, 'node')
    node.set(ATTR_ID, name)
    for attr in attrs:
        node.set(attr, str(attrs[attr]))
    return node


def remove_node_and_linked_edges(element_tree, name):
    """
    given an element tree, remove the first node with an id matching the given name.
    removal of nodes requires the removal of edges associated with the node.
    if node does not exist, nothing is removed.
    :param element_tree: the xml element representing the graph.
    :param name: name of the node.
    :return:
    """
    graph_element = element_tree.find("./" + GRAPH_TAG)
    if graph_element is None:
        raise AttributeError("root element must have an immediate child tagged 'graph'.")
    if name is None:
        raise AttributeError("node parameter cannot be None.")
    iter = graph_element.iterfind('node')
    for sub_element in iter:
        if sub_element.get(ATTR_ID) == name:
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
    nodes = graph_element.findall('./node')
    for sub_element in nodes:
        graph_element.remove(sub_element)
    remove_all_edges(element_tree)


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
    if source is None or dest is None:
        raise AttributeError("source and dest parameters must be existing nodes within the tree.")
    nodes = element_tree.findall("./" + GRAPH_TAG + '/' + NODE_TAG)
    source_node_exists = False
    dest_node_exists = False
    for node in nodes:
        if node.get(ATTR_ID) == source:
            source_node_exists = True
        if node.get(ATTR_ID) == dest:
            dest_node_exists = True
    if not (source_node_exists and dest_node_exists):
        raise AttributeError("source and dest parameters must be existing nodes within the tree.")
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
    if source is None or dest is None:
        raise AttributeError("source and dest parameters must be existing nodes within the tree.")
    iter = graph_element.iterfind('edge')
    for sub_element in iter:
        if sub_element.get(EDGE_SOURCE) == source and \
                sub_element.get(EDGE_DEST) == dest:
            graph_element.remove(sub_element)
            break
        elif sub_element.get(EDGE_SOURCE) == dest and \
                sub_element.get(EDGE_DEST) == source:
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
    edges = graph_element.findall('./edge')
    for sub_element in edges:
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

    # this regex will remove the graphml root element - but it can be remade easily.
    xml_entities = re.findall('</?(.*?)/?>', xml_string)
    for entity in xml_entities:
        if entity.strip()[0] == '?' and entity.strip()[-1] == '?':
            # xml header, not needed
            del entity
        elif entity[0] == '!':
            # possible ssi comment or doc / entity declaration - might be dangerous.
            del entity
        elif entity[0] == '/':
            # don't need ending tags
            del entity
    for index in range(len(xml_entities)):
        if xml_entities[index][-1] == '/':
            # remove end chars in self ending entities.
            xml_entities[index] = xml_entities[index][:-1]

    # collect important elements: graph doc, node elements, edge elements
    graph_entity = None
    node_tags = []
    edge_tags = []
    for entity in xml_entities:
        if entity[0:5] == GRAPH_TAG:
            graph_entity = entity
        elif entity[0:4] == NODE_TAG:
            node_tags.append(entity)
        elif entity[0:4] == EDGE_TAG:
            edge_tags.append(entity)

    if graph_entity is not None:
        _, name, edgedefault = graph_entity.split()
    else:
        _, name, edgedefault = "", "submodules.graphml", "undirected"

    # build the basic tree.
    if edgedefault == "undirected":
        directed = True
    elif edgedefault == "directed":
        directed = False
    else:
        directed = False
    tree = make_base_xml(name, directed)
    # get the doc and attach nodes and edges to it.
    doc = tree.find('./' + GRAPH_TAG)
    for node in node_tags:
        node_attribs = node.split()[1:]
        new_node = ET.SubElement(doc, NODE_TAG)
        for attr in node_attribs:
            tmp = attr.split('=')
            new_node.set(tmp[0], tmp[1])
    for edge in edge_tags:
        edge_attribs = edge.split()[1:]
        new_edge = ET.SubElement(doc, EDGE_TAG)
        for attr in edge_attribs:
            tmp = attr.split('=')
            new_edge.set(tmp[0], tmp[1])

    return tree




