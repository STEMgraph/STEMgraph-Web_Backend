# JSON-LD Structure: Exercise

**Type:** `https://schema.org/LearningResource`  
**Context:** `bin/ld-context.json`

## Properties

| Field | Type | Multiplicity | Description |
|-------|------|--------------|-------------|
| `@id` | String | 1 | The exercise's UUID. |
| `@type` | String | 1 | Always "Exercise". |
| `learningResourceType` | String | 1 | The kind of exercise, e.g. workshop, handout or just exercise. |
| `author` | Person | 1-n | The exercise's author(s). |
| `publishedAt` | Date | 1 | The date the exercise was published. |
| `keywords` | String | 0-n | Tags describing the exercise's content. |
| `teaches` | String | 1 | The competency a person taking this exercise is expected to learn. |
| `dependsOn` | String | 0-n | Exercises this one is based on. |

## structure of *author*'s list entries

| Field | Type | Multiplicity | Description |
|-------|------|--------------|-------------|
| `@type` | Person | 1 | Always "Person". |
| `name` | String | 1 | The author's name. |

## structure of *dependsOn* alternatives

| Field | Type | Multiplicity | Description |
|-------|------|--------------|-------------|
| `@type` | Class | 1 | Always "dependsOnAlternatives". |
| `oneOf` | String | 2-n | List of alternative prerequisite exercises. |

### Example

```jsonld
{
  "@id": "f87c7e89-ece7-4c55-af54-16a3b3b7435f",
  "@type": "Exercise",
  "learningResourceType": "Exercise",
  "author": [
    {
      "@type": "Person",
      "name": "Stephan Bökelmann"
    }
  ],
  "publishedAt": "2025-06-05",
  "keywords": [
    "C Compiler",
    "Inline Assembly",
    "Syscall",
    "Objdump",
    "Locals and Globals",
    "Primitive Types"
  ],
  "teaches": "C Compiler: Working with Primitive Types and Inspecting Binaries",
  "dependsOn": [
    "302c98a7-cbea-435c-ada2-bbf7538429a2",
    "81f2e303-d35c-4857-9cb7-190e3c5372b0",
    {
      "@type": "dependsOnAlternatives",
      "oneOf": [
        "718193ef-11a1-408d-af23-4b10c24d490d",
        "99787eda-617a-4a68-b9a4-d60ec5c5c303"
      ]
    }
  ]
}
