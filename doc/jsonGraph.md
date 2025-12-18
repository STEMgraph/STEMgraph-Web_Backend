# JSON-LD structure: Graph metadata

**Type:** `JSON-LD`  
**Context:** `bin/ld-context.json`

## Properties

| Field | Type | Multiplicity | Description |
|-------|------|--------------|-------------|
| `@id` | String | 1 | The URL where the graph was generated. |
| `generatedBy` | Organization | 1 | Who created this specific graph from raw data. |
| `generatedAt` | DateTime | 1 | The timestamp when the graph was created. |

## structure of *generatedBy*

| Field | Type | Multiplicity | Description |
|-------|------|--------------|-------------|
| `@type` | String | 1 | Always "schema:Organization". |
| `schema:name` | String | 1 | The creator's name. |
| `schema:url` | String | 1 | The creator's homepage. |

### Example

```jsonld
{
  "@id": "https://stemgraph-api.boekelmann.net/getWholeGraph",
  "generatedBy": {
    "@type": "schema:Organization",
    "schema:name": "STEMgraph",
    "schema:url": "https://github.com/STEMgraph"
  },
  "generatedAt": "2025-12-18T11:13:21.238404Z",
}