from collections import defaultdict
from services.graph_ld import get_ld_graph

# auxiliary functions to get lists and counts of tags

def get_count(field: str, subfield: str = None, lowercase: bool = True):
    """
    Returns frequency counts for a given field in the database.
    - field: top-level field in each exercise
    - subfield: optional subfield if field is a dict
    - lowercase: normalize values to lowercase if True
    """
    counts = defaultdict(int)
    db = get_ld_graph()
    for ex in db["@graph"]:
        if ex.get(field) is not None:
            field_values = ex[field]
            if isinstance(field_values, str) or isinstance(field_values, dict):
                field_values = [field_values]
            for value in field_values:
                if isinstance(value, dict) and subfield:
                    value = value.get(subfield)
                if value is None:
                    continue
                if lowercase and isinstance(value, str):
                    value = value.lower()
                counts[value] += 1
    return dict(counts)

def get_list(field: str, subfield: str = None, lowercase: bool = True):
    """
    Returns a list of unique values for a given field in the database.
    - field: top-level field in each exercise (e.g. "keywords", "author")
    - subfield: optional subfield if field is a dict (e.g. "name")
    - lowercase: normalize values to lowercase if True
    """
    values = set()
    db = get_ld_graph()
    for ex in db["@graph"]:
        if ex.get(field) is not None:
            field_values = ex[field]
            if isinstance(field_values, str) or isinstance(field_values, dict):
                field_values = [field_values]
            for value in field_values:
                if isinstance(value, dict) and subfield:
                    value = value.get(subfield)
                if value is None:
                    continue
                if lowercase and isinstance(value, str):
                    value = value.lower()
                values.add(value)
    return sorted(list(values))
