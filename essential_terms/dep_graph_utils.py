'''
    Util function working on dependency graph produced by spaCy.
    Features like degree centrality, betweenness centrality, etc.
    Check function below for more information. Words are always
    considered in their lower form when building dictionaries.
    E.g. flower not Flower, i not I, etc.
'''
import numpy as np
import spacy

from collections import deque


'''
nlp = spacy.load("en_core_web_sm")
doc = nlp("U.S.A economy has grown up by over 10% in the last year."
          "It is one of the most powerful countries in the world.")
doc = nlp("I love apples and pizza and water. She is my girlfriend."
          "Apples are very tasty. Wow! She and I are walking")
doc = nlp("She likes flowers. Flowers are beautiful. Me and she, flowers.")
doc = nlp("the dog and the woman love the dog")
doc = nlp("One way animals usually respond to a sudden drop in "
          "temperature is by ...")

spacy.displacy.serve(doc, style='dep')
'''


def _find_roots(doc):
    assert(isinstance(doc, spacy.tokens.doc.Doc))
    nodes = set()
    for token in doc:
        for x in token.children:
            nodes.add(x)
    roots = set()
    for token in doc:
        if token not in nodes:
            roots.add(token)
    return roots


def _to_softmax(x):
    assert(isinstance(x, dict))
    softmax_sum = 0.0
    for word in x:
        softmax_sum += np.exp(x[word])
    for word in x:
        x[word] = 1.0 * np.exp(x[word]) / softmax_sum
    return x


def _build_distance_matrix(node_idx, nodes):
    assert(len(node_idx) == len(nodes))
    num_nodes = len(nodes)
    adj = [[0 for j in range(0, num_nodes)] for i in range(0, num_nodes)]

    for start_node in nodes:
        # Start a BFS from each node.
        q = deque()
        q.append(start_node)
        dist = {}
        dist[start_node] = 0
        while len(q) >= 1:
            node = q.popleft()
            for child in node.children:
                if child in dist:
                    continue
                dist[child] = dist[node] + 1
                q.append(child)
            if node.head not in dist:
                dist[node.head] = dist[node] + 1
                q.append(node.head)
        dist_idx = {}
        for node in nodes:
            dist_idx[node_idx[node]] = dist[node]
        for i in range(0, num_nodes):
            adj[node_idx[start_node]][i] = dist_idx[i]

    for i in range(0, num_nodes):
        assert(sum(1 for x in adj[i] if x == 0) == 1)

    for i in range(0, num_nodes):
        for j in range(0, num_nodes):
            assert(adj[i][j] == adj[j][i])
    return adj


def _build_adjacency_matrix(node_idx, nodes):
    assert(len(node_idx) == len(nodes))
    num_nodes = len(nodes)
    adj = [[0 for j in range(0, num_nodes)] for i in range(0, num_nodes)]
    for node in nodes:
        for child in node.children:
            adj[node_idx[node]][node_idx[child]] = 1.0
            adj[node_idx[child]][node_idx[node]] = 1.0

    for i in range(0, num_nodes):
        for j in range(0, num_nodes):
            assert(adj[i][j] == adj[j][i])
    return adj


# dict (word -> avg. degree centrality).
def build_degree_centrality(doc):
    roots = _find_roots(doc)
    deg = {}
    for token in doc:
        word = token.lower_
        d = 0
        for _ in token.children:  # This is a generator. No len() defined.
            d += 1
        if token not in roots:
            d += 1
        if word not in deg:
            deg[word] = []
        deg[word].append(d)
    for word in deg:
        if len(deg[word]) == 0:
            deg[word] = 0.0
        else:
            deg[word] = 1.0 * sum(deg[word]) / len(deg[word])
    return _to_softmax(deg)


def build_closeness_centrality(doc):
    roots = _find_roots(doc)
    dist = {}
    for root in roots:
        nodes = []
        for x in root.subtree:
            nodes.append(x)
        assert(len(nodes) == len(set(nodes)))
        node_idx = {nodes[i]: i for i in range(0, len(nodes))}
        assert(len(nodes) == len(node_idx))
        adj = _build_distance_matrix(node_idx, nodes)
        for node in nodes:
            idx = node_idx[node]
            word = node.lower_
            closeness = 1.0 * (len(nodes) - 1.0) / max(sum(adj[idx]), 1.0)
            if word not in dist:
                dist[word] = []
            dist[word].append(closeness)
    for word in dist:
        if len(dist[word]) == 0:
            dist[word] = 0.0
        else:
            dist[word] = 1.0 * sum(dist[word]) / len(dist[word])
    return dist


def build_eigenvector_centrality(doc):
    roots = _find_roots(doc)
    dist = {}
    for root in roots:
        nodes = []
        for x in root.subtree:
            nodes.append(x)
        assert(len(nodes) == len(set(nodes)))
        node_idx = {nodes[i]: i for i in range(0, len(nodes))}
        assert(len(nodes) == len(node_idx))
        adj = _build_adjacency_matrix(node_idx, nodes)
        adj = np.matrix(adj)
        num_nodes = len(nodes)
        eigenvalues, eigenvectors = np.linalg.eigh(adj)
        assert(eigenvalues.shape == (num_nodes,))
        assert(eigenvectors.shape == (num_nodes, num_nodes))

        # Find the dominant eigenvalue (and eigenvector).
        max_eigenvalue = None
        max_eigenvector = None
        for i in range(0, num_nodes):
            if max_eigenvalue is None or eigenvalues[i] > max_eigenvalue:
                max_eigenvalue = eigenvalues[i]
                max_eigenvector = eigenvectors[:, i]
        max_eigenvector = np.asarray(max_eigenvector).flatten()

        # The dominant eigenvector should be all positive or all negative.
        if np.where(max_eigenvector > 0.0)[0].shape[0] == 0:
            max_eigenvector = -max_eigenvector
        assert(np.where(max_eigenvector >= 0.0)[0].shape[0] == num_nodes)
        assert(np.allclose(np.linalg.norm(max_eigenvector), 1.0))

        for node in nodes:
            idx = node_idx[node]
            word = node.lower_
            if word not in dist:
                dist[word] = max_eigenvector[idx]
            else:
                dist[word] = max(dist[word], max_eigenvector[idx])
    return dist


'''
for token in doc:
    l = []
    for x in token.children:
        l.append(x)
    print(token, l)
    print(build_eigenvector_centrality(doc))
'''
