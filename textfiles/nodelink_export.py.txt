from formats.base_export import GraphExporter


class NodeLinkExporter(GraphExporter):

    def from_ld(self, ld_data: dict):
        """
        Konvertiert eine JSON-LD Datenstruktur in Node-Link-Format.
        Erwartet ein dict mit '@graph': [...]
        """

        nl = {"nodes": [], "links": []}

        if "@graph" not in ld_data:
            return nl

        # 1. Nodes erzeugen
        for ex in ld_data["@graph"]:
            node = {
                "id": ex.get("@id"),
                "type": ex.get("@type", "Exercise"),
                "teaches": ex.get("teaches"),
                "author": [a.get("name") for a in ex.get("author", [])] if isinstance(ex.get("author"), list) else [],
                "keywords": ex.get("keywords"),
                "publishedAt": ex.get("publishedAt")
            }
            nl["nodes"].append(node)

        # 2. Links erzeugen
        for ex in ld_data["@graph"]:
            target = ex.get("@id")
            deps = ex.get("dependsOn", [])

            for dep in deps:
                # einfacher String
                if isinstance(dep, str):
                    nl["links"].append({"source": dep, "target": target})

                # oneOf-Alternative
                elif isinstance(dep, dict) and dep.get("oneOf"):
                    for alt in dep["oneOf"]:
                        nl["links"].append({"source": alt, "target": target})

        return nl

    def load(self):
        raise NotImplementedError("Use from_ld() instead")

    def filter(self, **criteria):
        raise NotImplementedError("Filtering happens in JSON-LD")

    def export(self):
        raise NotImplementedError("Use from_ld() instead")
