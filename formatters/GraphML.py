__author__ = 'Roland'

import xml.etree.cElementTree as ET
from xml.dom import minidom

XSI = 'xsi'
SCHEMA_LOCATION = 'schemaLocation'
GRAPHML_TAG = 'graphml'

NODE_TAG = 'node'
EDGE_TAG = 'edge'
EDGE_SOURCE = "source"
EDGE_DEST = "target"


def make_base_xml():
    """
    generate the root and graph elements used by GraphML
    :return: root and graph elements, in that order
    """
    ROOT_ELEMENT = ET.Element(GRAPHML_TAG)
    ROOT_ELEMENT.set("xmlns", "http://graphml.graphdrawing.org/xmlns")
    ROOT_ELEMENT.set("xmlns" + ":" + XSI, "http://graphml.graphdrawing.org/xmlns")
    ROOT_ELEMENT.set(XSI + ":" + SCHEMA_LOCATION, "http://graphml.graphdrawing.org/xmlns\n" +
                     "http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd")
    GRAPH_ELEMENT = ET.SubElement(ROOT_ELEMENT, "graph")
    GRAPH_ELEMENT.set("id", __name__)
    GRAPH_ELEMENT.set("edgedefault", "undirected")
    return ROOT_ELEMENT, GRAPH_ELEMENT


def make_node(graph_element, name, **attrs):
    """
    generate a node element, given a graph element to attach to.
    :param graph_element: the xml element representing the graph
    :param name: name of the node
    :param attrs: attributes to attach to the node, as key -> value pairs
    :return: the node xml element
    """
    node = ET.SubElement(graph_element, 'node')
    node.set("id", name)
    for attr in attrs:
        node.set(attr, str(attrs[attr]))
    return node


def make_edge(graph_element, source, dest, **attrs):
    """
    generate an edge element, given a graph element to attach to.
    :param graph_element: the xml element representing the graph
    :param source: first node of the edge.
    :param dest: second node of the edge.
    :param attrs: attributes to attach to the edge, as key -> value pairs
    :return: the node xml element
    """
    edge = ET.SubElement(graph_element, 'edge')
    edge.set(EDGE_SOURCE, source)
    edge.set(EDGE_DEST, dest)
    for attr in attrs:
        edge.set(attr, str(attrs[attr]))
    return edge


def build_xml_to_string(xml_root):
    """
    given the root of an xml tree, convert the xml to a formatted string
    :param xml_root: xml root element to parse from
    :return: a prettified string containing formatted xml
    """
    xml_string = ET.tostring(xml_root, 'utf-8')
    xml_string = '<?xml version="1.0" encoding="UTF-8"?>\n' + xml_string
    reparsed_string = minidom.parseString(xml_string)
    return reparsed_string.toprettyxml(indent="\t")

