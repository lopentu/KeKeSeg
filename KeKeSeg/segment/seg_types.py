
class GranSeg:
    def __init__(self, G):
        self.G = G
        self.level = 1
        self.seg_edges = {}

    def copy(self):
        newG = (self.G[0].copy(), self.G[1].copy())
        g = GranSeg(newG)
        g.level = self.level
        return g

    def to_segments(self):
        segs = []
        poses = []
        nodes = self.G[0]

        seg_edges = self.seg_edges
        for edge_x, edge_data in seg_edges.items():
            start_idx, end_idx = edge_x
            # breakpoint()
            mwe = ''.join(nodes.get(i, [""])[0] for i in range(start_idx, end_idx))
            segs.append(mwe)
            poses.append(edge_data.get("pos", ""))
        return list(zip(segs, poses))

    def apply_seg_edges(self):
        self.seg_edges = self.G[1]

    def __repr__(self):
        if self.seg_edges:
            tokens = ["_".join(x) for x in self.to_segments()]
            repr_seq = "/".join(tokens)
            return f"<GranSeg: {self.level}>: {repr_seq}" 
        else:
            return f"<GranSeg: {self.level} (not seged)> {''.join(x[0] for x in self.G[0].values())}"

    @property
    def nodes(self):
        return self.G[0]
    
    @property
    def edges(self):
        return self.G[1]