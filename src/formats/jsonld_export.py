from formats.base_export import GraphExporter

class JsonLDExporter(GraphExporter):

    def from_ld(self, ld_data):
        return ld_data

    def load(self):
        raise NotImplementedError()

    def filter(self, **criteria):
        raise NotImplementedError()

    def export(self):
        raise NotImplementedError()

