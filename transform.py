import pandas as pd
import xml.etree.ElementTree as ET

file_prefix = '../TransportationNetworks/Berlin-Center/Berlin-Center'

nodes = pd.read_csv(open(file_prefix + '_node.tntp'), delimiter='[\s\t]+')

nodes_root = ET.Element('nodes')
nodes_tree = ET.ElementTree(nodes_root)

for node in nodes.values:
    n = ET.SubElement(nodes_root, 'node', attrib={'id': str(node[0]), 'x': str(node[1]*1609), 'y': str(node[2]*1609)})

nodes_tree.write('berlin-center.nod.xml')

edges = pd.read_csv(open(file_prefix + '_net.tntp'), delimiter='[\t]+', comment='<')

edges_root = ET.Element('edges')
edges_tree = ET.ElementTree(edges_root)

# Init node,    Term node,  Capacity,   Length, Free Flow Time, B,  Power,  Speed limit,    Toll,   Link Type;
# 0             1           2           3       4               5   6       7               8       9

for edge in enumerate(edges.values):
    attribs = {'id': str(edge[0]),
               'from': str(edge[1][0]),
               'to': str(edge[1][1]),
               'type': str(edge[1][9]),
               'length': str(edge[1][3]),
               }
    e = ET.SubElement(edges_root, 'edge', attrib=attribs)

edges_tree.write('berlin-center.edg.xml')