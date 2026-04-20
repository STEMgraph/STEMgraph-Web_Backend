class GraphExporter:
    def load(self):
        """Lädt die Graphdaten aus dem jeweiligen Format."""
        raise NotImplementedError

    def filter(self, **criteria):
        """Filtert die Daten nach author, keyword, topic usw."""
        raise NotImplementedError

    def export(self):
        """Gibt die Daten im jeweiligen Format zurück."""
        raise NotImplementedError
