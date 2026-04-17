import yaml
from formats.base_export import GraphExporter
from services import graph_ld  # YAML basiert auf LD-Struktur

class YamlExporter(GraphExporter):
    def load(self):
        return graph_ld.get_ld_graph()

    def filter(self, **criteria):
        # später: Filterlogik einbauen
        return graph_ld.get_ld_graph()

    def export(self):
        data = self.load()
        return yaml.dump(data, allow_unicode=True)
