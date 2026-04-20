import yaml
from formats.base_export import GraphExporter

class YamlExporter(GraphExporter):

    def from_ld(self, ld_data):
        """
        Konvertiert JSON-LD Daten in YAML-Format.
        """
        return yaml.dump(ld_data, allow_unicode=True, default_flow_style=False)

    def load(self):
        raise NotImplementedError()

    def filter(self, **criteria):
        raise NotImplementedError()

    def export(self):
        raise NotImplementedError()
