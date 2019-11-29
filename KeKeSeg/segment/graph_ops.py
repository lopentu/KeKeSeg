import re
import math
from zhon import hanzi
from .lexicon import Lexicon

def tokenizer(text):
    token_pat = re.compile(rf"[{hanzi.characters}]|[^{hanzi.characters}\s]+|[\s]+")
    tokens = []
    for mat in token_pat.finditer(text):
        tokens.append((mat.group(), mat.start(), mat.end()))
    return tokens

def build_graph(text, lexicon: Lexicon):
    tokens = tokenizer(text)    
    nodes = {x[1]: x for x in tokens}
    node_ids = list(nodes.keys())
    edges = {(n_x, n_y): {"freq": 0.5} for n_x, n_y in zip(node_ids, node_ids[1:])}
    for start_idx, tok in enumerate(tokens):
        ch = tok[0]
        leading_words = lexicon.prefixes(ch)
        for end_idx in range(len(tokens), start_idx, -1):
            tok_seq = tokens[start_idx:end_idx]
            chseq = ''.join([x[0] for x in tok_seq])
            if chseq in leading_words:    
                if len(chseq) == 1: continue
                start_node = start_idx
                end_node = tok_seq[-1][2]
                edges[(start_node, end_node)] = {
                    "freq": leading_words[chseq]
                }
    return (nodes, edges)

def build_colligation_graph(G, lexicon: Lexicon, win=2):
    cG = G.copy()
    cG.level = win
    edges = cG.edges
    edges_id = sorted(edges, key=lambda x: x[0])
    
    for idx in range(0, len(edges_id)):
        start_edge_i = idx
        end_edge_i = idx+win
        if end_edge_i >= len(edges_id):
            break

        pos_list = [edges.get(eid, {}).get("pos", "X") 
                    for eid in edges_id[start_edge_i:end_edge_i]]
        collig_freq = lexicon.colligation_freq(pos_list)

        start_node = edges_id[start_edge_i][0]
        end_node = edges_id[end_edge_i-1][1]
        edges[(start_node, end_node)] = {
            "freq": collig_freq, "type": "colligation", "pos": "(MWE)"
        }
    
    return cG

def find_neighbors(node, edges):
    neighbors = []
    for edge_x in edges:
        if node == edge_x[0]:
            neighbors.append(edge_x[1])
    return neighbors

def dijkstra(graph):
    nodes, edges = graph
    node_ids = sorted(nodes.keys())
    unvisited = node_ids.copy()
    unvisited.reverse()
    distances = {}
    backpointers = {}

    while unvisited:
        node_x = unvisited.pop()
        neighbors = find_neighbors(node_x, edges)
        for node_y in neighbors:
            edge_weight = edges.get((node_x, node_y), {}).get("freq", 0)
            edge_score = ((node_y-node_x)**2) * math.log(edge_weight+1)
            dist_new = distances.get(node_x, 0) + edge_score

            if dist_new > distances.get(node_y, 0):
                distances[node_y] = dist_new
                backpointers[node_y] = node_x

    last_nodes = node_ids[-1]
    last_tok_end = nodes[last_nodes][2]
    prev = backpointers.get(last_nodes)
    path = [last_tok_end, last_nodes]
    
    while prev is not None:
        path.append(prev)
        prev = backpointers.get(prev)
    path.reverse()

    return path
    


    


