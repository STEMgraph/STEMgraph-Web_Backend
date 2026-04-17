from formats.base_export import GraphExporter
from services.graph_nl import get_nodelink_graph

class NodeLinkExporter(GraphExporter):
    def load(self):
        return get_nodelink_graph()

    def filter(self, **criteria):
        return self.load()

    def export(self):
        return self.load()
