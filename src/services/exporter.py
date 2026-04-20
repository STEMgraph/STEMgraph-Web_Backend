from fastapi.responses import JSONResponse
from formats.jsonld_export import JsonLDExporter
from formats.nodelink_export import NodeLinkExporter
from formats.yaml_export import YamlExporter   # falls vorhanden

def export_graph(ld_data, format: str):
    """
    Einheitliche Export-Pipeline für alle Ausgabeformate.
    ld_data: JSON-LD Datenstruktur (dict)
    format: 'jsonld' | 'nodelink' | 'yaml'
    """

    if format == "jsonld":
        return JSONResponse(
            content=ld_data,
            media_type="application/ld+json"
        )

    elif format == "nodelink":
        nl = NodeLinkExporter().from_ld(ld_data)
        return JSONResponse(
            content=nl,
            media_type="application/json"
        )

    elif format == "yaml":
        yaml = YamlExporter().from_ld(ld_data)
        return JSONResponse(
            content=yaml,
            media_type="text/yaml"
        )

    else:
        return JSONResponse(
            content={"error": f"Unknown format '{format}'"},
            status_code=400
        )
