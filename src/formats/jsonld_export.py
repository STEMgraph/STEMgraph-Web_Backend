from formats.base_export import GraphExporter
from services.graph_ld import load_ld_database

class JsonLDExporter(GraphExporter):
    def load(self):
        return load_ld_database()

    def filter(self, **criteria):
        return self.load()

    def export(self):
        return self.load()
