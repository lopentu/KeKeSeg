import pickle
from collections import namedtuple

GranSegLexicon = namedtuple("GranSegLexicon", 
    ["ch_freq", "wd_freq", "pos_bg_freq", "pos_tg_freq", "wd_pos", "ch_pos"])

class Lexicon:
    def __init__(self):
        self.d = None
    
    def load_data(self, data_path):
        with data_path.open("rb") as fin:
            data = pickle.load(fin)
            self.d = GranSegLexicon(
                data["ch_freq"], data["wd_freq"],
                data["pos_bg_freq"], data["pos_tg_freq"],
                data["wd_pos"], data["ch_pos"]
            )
        self.index_words()
    
    def index_words(self):
        word_index = {}
        for wd, _ in self.d.wd_freq.items():
            word_index.setdefault(wd[0], []).append(wd)
        self.word_index = word_index

    def prefixes(self, charac):
        words = self.word_index.get(charac, [])
        ret_dat = {w: self.d.wd_freq.get(w, 0) for w in words}
        return ret_dat
    
    def colligation_freq(self, poses):
        if isinstance(poses, list):
            poses = tuple(poses)

        if len(poses) == 2:
            freq = self.d.pos_bg_freq.get(poses, 0)
        elif len(poses) == 3:
            freq = self.d.pos_tg_freq.get(poses, 0)
        else:
            freq = 0

        return freq
        
    @property
    def word_pos(self):
        return self.d.wd_pos



        