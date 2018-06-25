import collections

import xml.etree.ElementTree as ET
import numpy as np


Trip = collections.namedtuple('Trip', ['id', 'depart', 'fr', 'to'])

X, Y = 4, 4
start = 0
end = 3600

NS_lam = 4
EW_lam = 4

same_row_prob = 0.5
same_col_prob = 0.5

trips_root = ET.Element('trips')
trips_tree = ET.ElementTree(trips_root)

E_in = [f'edge-1:{j}/0:{j}' for j in range(Y)]
W_in = [f'edge{X}:{j}/{X-1}:{j}' for j in range(Y)]
EW_in = E_in + W_in


S_in = [f'edge{j}:-1/{j}:0' for j in range(Y)]
N_in = [f'edge{j}:{Y}/{j}:{Y-1}' for j in range(Y)]
NS_in = S_in + N_in

in_edges = EW_in + NS_in

E_out = [f'edge0:{j}/-1:{j}' for j in range(Y)]
W_out = [f'edge{X-1}:{j}/{X}:{j}' for j in range(Y)]
EW_out = E_out + W_out

S_out = [f'edge{j}:0/{j}:-1' for j in range(Y)]
N_out = [f'edge{j}:{Y-1}/{j}:{Y}' for j in range(Y)]
NS_out = N_out + S_out
out_edges = EW_out + NS_out

print(','.join(out_edges))

print('Ei', E_in)
print('Wi', W_in)
print('Si', S_in)
print('Ni', N_in)
print('Eo', E_out)
print('Wo', W_out)
print('So', S_out)
print('No', N_out)

trp_id = 0

trips = []

for in_edg in EW_in:
    current_time = start

    while current_time < end:
        current_time += np.random.poisson(4)
        trp_id += 1
        to = ''
        if in_edg in E_in:
            if np.random.rand() < same_row_prob:
                to = W_out[E_in.index(in_edg)]
            else:
                to = W_out[np.random.randint(0, len(W_out))]

        if in_edg in W_in:
            if np.random.rand() < same_row_prob:
                to = E_out[W_in.index(in_edg)]
            else:
                to = E_out[np.random.randint(0, len(E_out))]

        attrs = {'id': str(trp_id),
                 'depart': str(current_time),
                 'fr': in_edg,
                 'to': to}

        trips.append(Trip(**attrs))

for in_edg in NS_in:
    current_time = start

    while current_time < end:
        current_time += np.random.poisson(4)
        trp_id += 1
        to = ''
        if in_edg in N_in:
            if np.random.rand() < same_row_prob:
                to = S_out[N_in.index(in_edg)]
            else:
                to = S_out[np.random.randint(0, len(S_out))]

        if in_edg in S_in:
            if np.random.rand() < same_col_prob:
                to = N_out[S_in.index(in_edg)]
            else:
                to = N_out[np.random.randint(0, len(N_out))]


        attrs = {'id': str(trp_id),
                 'depart': str(current_time),
                 'fr': in_edg,
                 'to': to}
        trips.append(Trip(**attrs))


for trp in sorted(trips, key = lambda x: x.depart):
    attrs = {'id': trp.id,
             'depart': trp.depart,
             'from': trp.fr,
             'to': trp.to}
    ET.SubElement(trips_root, 'trip', attrib=attrs)


trips_tree.write('grid2.trips.xml')