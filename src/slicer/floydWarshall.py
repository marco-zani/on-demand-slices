def     initMatrix(n,prf_devices, devices):
    out = [[float('inf')] * n for _ in range(n)]
    for el in prf_devices:
        for _, endDev in devices[el]:
            if endDev in prf_devices:
                out[prf_devices.index(el)][prf_devices.index(endDev)] = 1
    return out

def shrinkTable(matrix, devices):
    n = len(matrix)
    out = [[] for _ in range(n)]

    x = 0
    while x < n:
        y = 0
        while y < n:
            if(x != y):
                index = -1
                j = 0
                while j < len(out[x]) and index == -1:
                    if out[x][j][0] == devices[matrix[x][y]]:
                        index = j
                    j += 1
                if index == -1:
                    out[x].append((devices[int(matrix[x][y])],[devices[y]]))
                else:
                    out[x][index][1].append(devices[y])
            y += 1
        x+=1
    
    return out

def extractSwitches(matrix):
    out = {}

    for name in matrix:
        if name[0] == 's':
            out.update({name:matrix[name]})

    return out

        
def compute_next_hop(adjMatrix):
    n = len(adjMatrix)
    next_hop = [[-1] * n for _ in range(n)]

    # Initialize the next_hop matrix based on direct edges
    for i in range(n):
        for j in range(n):
            if i != j and adjMatrix[i][j] != float('inf'):
                next_hop[i][j] = j

    # Floyd-Warshall algorithm
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if adjMatrix[i][k] + adjMatrix[k][j] < adjMatrix[i][j]:
                    adjMatrix[i][j] = adjMatrix[i][k] + adjMatrix[k][j]
                    next_hop[i][j] = next_hop[i][k]

    return next_hop

def convertToDict(matrix, devices):
    out = {}
    for el in matrix:
        out.update({devices[matrix.index(el)]:el})
    return out

def add_min_bandwidth(conf, percentages):
    slice_index_1 = 0
    for _,slice1 in conf:
        slice_index_2 = 0
        for _,slice2 in conf:
            if slice1 != slice2:
                for sw1 in slice1:
                    for sw2 in slice2:
                        if sw1 == sw2:
                            port_index_1 = 0
                            for (port1, perc1), hosts1 in slice1[sw1]:
                                port_index_2 = 0
                                for (port2, _), _ in slice2[sw2]:
                                    if port1 == port2:
                                        conf[slice_index_1][1][sw1][port_index_1] = (port1, perc1-percentages[slice_index_2]), hosts1
                                    port_index_2 += 1
                                port_index_1 += 1
            slice_index_2 += 1
        slice_index_1 += 1