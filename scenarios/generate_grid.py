import xml.etree.ElementTree as ET

X, Y = 4, 4

nodes_root = ET.Element('nodes')
nodes_tree = ET.ElementTree(nodes_root)

for i in range(-1, X+1):
    for j in range(-1, Y+1):
        attributes = {'id': f'node{i}:{j}',
                      'x': str(100+300*i) if 0 <= i < X else '0' if i <= 0 else str(300*(i-1)+200),
                      'y': str(100+300*j) if 0 <= j < Y else '0' if j <= 0 else str(300*(j-1)+200),
                      'type': 'traffic_light'}
        n = ET.SubElement(nodes_root, 'node', attrib=attributes)

edges_root = ET.Element('edges')
edges_tree = ET.ElementTree(edges_root)

connections_root = ET.Element('connections')
connections_tree = ET.ElementTree(connections_root)

def generate_connections(root, i, j):
    attributes = {'from': f'edge{i-1}:{j}/{i}:{j}.-45', # E -> S
                  'to': f'edge{i}:{j}/{i}:{j-1}',
                  'fromLane': '0',
                  'toLane': '0'
                }
    c = ET.SubElement(root, 'connection', attrib=attributes)
    attributes = {'from': f'edge{i-1}:{j}/{i}:{j}.-45', # E -> W
                  'to': f'edge{i}:{j}/{i+1}:{j}',
                  'fromLane': '0',
                  'toLane': '0'
                  }
    c = ET.SubElement(root, 'connection', attrib=attributes)
    attributes = {'from': f'edge{i-1}:{j}/{i}:{j}.-45', # E -> W
                  'to': f'edge{i}:{j}/{i+1}:{j}',
                  'fromLane': '1',
                  'toLane': '1'
                  }
    c = ET.SubElement(root, 'connection', attrib=attributes)
    attributes = {'from': f'edge{i-1}:{j}/{i}:{j}.-45', # E -> N
                  'to': f'edge{i}:{j}/{i}:{j+1}',
                  'fromLane': '2',
                  'toLane': '0'
                  }
    c = ET.SubElement(root, 'connection', attrib=attributes)

    attributes = {'from': f'edge{i}:{j-1}/{i}:{j}.-45', # S -> E
                  'to': f'edge{i}:{j}/{i+1}:{j}',
                  'fromLane': '0',
                  'toLane': '0'
                  }
    c = ET.SubElement(root, 'connection', attrib=attributes)
    attributes = {'from': f'edge{i}:{j-1}/{i}:{j}.-45', # S -> N
                  'to': f'edge{i}:{j}/{i}:{j+1}',
                  'fromLane': '0',
                  'toLane': '0'
                  }
    c = ET.SubElement(root, 'connection', attrib=attributes)
    attributes = {'from': f'edge{i}:{j-1}/{i}:{j}.-45',
                  'to': f'edge{i}:{j}/{i}:{j+1}',       # S -> N
                  'fromLane': '1',
                  'toLane': '1'
                  }
    c = ET.SubElement(root, 'connection', attrib=attributes)
    attributes = {'from': f'edge{i}:{j-1}/{i}:{j}.-45',
                  'to': f'edge{i}:{j}/{i-1}:{j}',       # S -> E
                  'fromLane': '2',
                  'toLane': '1'
                  }
    c = ET.SubElement(root, 'connection', attrib=attributes)

    attributes = {'from': f'edge{i+1}:{j}/{i}:{j}.-45', # E -> N
                  'to': f'edge{i}:{j}/{i}:{j+1}',
                  'fromLane': '0',
                  'toLane': '0'
                  }
    c = ET.SubElement(root, 'connection', attrib=attributes)
    attributes = {'from': f'edge{i+1}:{j}/{i}:{j}.-45', # E -> W
                  'to': f'edge{i}:{j}/{i-1}:{j}',
                  'fromLane': '0',
                  'toLane': '0'
                  }
    c = ET.SubElement(root, 'connection', attrib=attributes)
    attributes = {'from': f'edge{i+1}:{j}/{i}:{j}.-45', # E -> W
                  'to': f'edge{i}:{j}/{i-1}:{j}',
                  'fromLane': '1',
                  'toLane': '1'
                  }
    c = ET.SubElement(root, 'connection', attrib=attributes)
    attributes = {'from': f'edge{i+1}:{j}/{i}:{j}.-45', # E -> S
                  'to': f'edge{i}:{j}/{i}:{j-1}',
                  'fromLane': '2',
                  'toLane': '0'
                  }
    c = ET.SubElement(root, 'connection', attrib=attributes)

    attributes = {'from': f'edge{i}:{j+1}/{i}:{j}.-45', # N -> W
                  'to': f'edge{i}:{j}/{i-1}:{j}',
                  'fromLane': '0',
                  'toLane': '0'
                  }
    c = ET.SubElement(root, 'connection', attrib=attributes)
    attributes = {'from': f'edge{i}:{j+1}/{i}:{j}.-45', # N -> S
                  'to': f'edge{i}:{j}/{i}:{j-1}',
                  'fromLane': '0',
                  'toLane': '0'
                  }
    c = ET.SubElement(root, 'connection', attrib=attributes)
    attributes = {'from': f'edge{i}:{j+1}/{i}:{j}.-45', # N -> S
                  'to': f'edge{i}:{j}/{i}:{j-1}',
                  'fromLane': '1',
                  'toLane': '1'
                  }
    c = ET.SubElement(root, 'connection', attrib=attributes)
    attributes = {'from': f'edge{i}:{j+1}/{i}:{j}.-45', # N -> E
                  'to': f'edge{i}:{j}/{i+1}:{j}',
                  'fromLane': '2',
                  'toLane': '0'
                  }
    c = ET.SubElement(root, 'connection', attrib=attributes)

split1_attr = {'pos': '0', 'lanes': '0 1'}
split2_attr = {'pos': '-45', 'lanes': '0 1 2'}

for i in range(-1, X):
    for j in range(-1, Y):
        if j >= 0:
            attributes = {'id': f'edge{i}:{j}/{i+1}:{j}',
                          'from': f'node{i}:{j}',
                          'to': f'node{i+1}:{j}',
                          'numLanes': '3'}
            e = ET.SubElement(edges_root, 'edge', attrib=attributes)
            ET.SubElement(e, 'split', attrib=split1_attr)
            ET.SubElement(e, 'split', attrib=split2_attr)
            attributes = {'id': f'edge{i+1}:{j}/{i}:{j}',
                          'from': f'node{i+1}:{j}',
                          'to': f'node{i}:{j}',
                          'numLanes': '3'}
            e = ET.SubElement(edges_root, 'edge', attrib=attributes)
            ET.SubElement(e, 'split', attrib=split1_attr)
            ET.SubElement(e, 'split', attrib=split2_attr)
        if i >= 0:
            attributes = {'id': f'edge{i}:{j}/{i}:{j+1}',
                          'from': f'node{i}:{j}',
                          'to': f'node{i}:{j+1}',
                          'numLanes': '3'}
            e = ET.SubElement(edges_root, 'edge', attrib=attributes)
            ET.SubElement(e, 'split', attrib=split1_attr)
            if j < Y:
                ET.SubElement(e, 'split', attrib=split2_attr)
            attributes = {'id': f'edge{i}:{j+1}/{i}:{j}',
                          'from': f'node{i}:{j+1}',
                          'to': f'node{i}:{j}',
                          'numLanes': '3'}
            e = ET.SubElement(edges_root    , 'edge', attrib=attributes)
            ET.SubElement(e, 'split', attrib=split1_attr)
            ET.SubElement(e, 'split', attrib=split2_attr)
        if 0 <= i < X and 0 <= j < Y:
            generate_connections(connections_root, i, j)


nodes_tree.write('grid2.nod.xml')
edges_tree.write('grid2.edg.xml')
connections_tree.write('grid2.con.xml')
