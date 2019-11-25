import re
from zhon import hanzi
from pathlib import Path
from . import graph_ops as go
from .seg_types import GranSeg
from .lexicon import Lexicon

class Segmenter:
    def __init__(self, lexicon=None):
        if lexicon:
            self.lexicon = lexicon   
        else:
            self.lexicon = Lexicon()
            self.lexicon.load_data(Path(__file__).parent / "data/gran_seg_lexicon.pkl")
        self.notzhpat = re.compile(rf"[^{hanzi.characters}]+")

    def __segment_graph(self, text):
        G = go.build_graph(text, self.lexicon)
        shortest_path = go.dijkstra(G)
        segs = []

        word_edges = {}
        for s, e in zip(shortest_path, shortest_path[1:]):
            segs.append(text[s:e])
        pos_list = self.postag(segs)

        for i, (s, e) in enumerate(zip(shortest_path, shortest_path[1:])):
            word = text[s:e]
            word_edges[(s, e)] = {
                "freq": self.lexicon.d.wd_freq.get(word, 0),
                "pos": pos_list[i]
            }
        
        G = (G[0], word_edges)        

        return G, segs, pos_list

    def granseg(self, text):
        tG, _, _ = self.__segment_graph(text)
        G = GranSeg(tG)
        G.apply_seg_edges()
        return G
    
    def coarse(self, G: GranSeg, level=2):
        coll_g = go.build_colligation_graph(G, self.lexicon, win=level)
        shortest_path = go.dijkstra((coll_g.nodes, coll_g.edges))
        new_edges = {}        
        for s, e in zip(shortest_path, shortest_path[1:]):
            new_edges[(s,e)] = coll_g.edges[(s,e)]
        coarse_G = GranSeg((coll_g.nodes.copy(), new_edges))
        coarse_G.apply_seg_edges()
        coarse_G.level = level
        return coarse_G
        

    def segment(self, text):
        _, segs, pos_list = self.__segment_graph(text)
        ret_seq = list(zip(segs, pos_list))
        return ret_seq
    
    def postag(self, words):
        return [self.single_postag(x) for x in words]
    
    def single_postag(self, word):
        wd_pos = self.lexicon.word_pos
        pos_probs = wd_pos.get(word, {})
        pos_list = self.get_max_valued_key(pos_probs)
        if not word.strip():
            return "WHITESPACE"
        if self.notzhpat.match(word):
            return "FW"

        if not pos_list:
            buf = {}
            for ch in word:
                ch_pos = wd_pos.get(ch, {})
                for pos_x, prob in ch_pos.items():
                    buf[pos_x] = buf.get(pos_x, 0) + prob
            pos_list = self.get_max_valued_key(buf)
        if not pos_list:
            pos_list = "Na"
           
        return pos_list

    def constructions(self, tokens, gran_level=1):
        pass

    def multiseg(self, text):
        pass

    def get_max_valued_key(self, x: dict):
        if x:
            sort_keys = sorted(x.keys(), key=x.get, reverse=True)
            return sort_keys[0]
        return x
        
