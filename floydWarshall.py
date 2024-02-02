def initMatrix(n,prf, devices):
    out = [[float('inf')] * n for _ in range(n)]
    for el in prf:
        for _, endDev in devices[el]:
            if endDev in prf:
                out[prf.index(el)][prf.index(endDev)] = 1
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