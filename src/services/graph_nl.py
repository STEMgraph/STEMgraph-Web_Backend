from services.graph_ld import load_ld_database

def ld_to_nodelink(ld_data):
    """Konvertiert JSON-LD in Node-Link."""
    pass

def get_nodelink_graph():
    ld = load_ld_database()
    return ld_to_nodelink(ld)
