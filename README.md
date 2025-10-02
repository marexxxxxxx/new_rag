benötigt für den vektor index:
CREATE VECTOR INDEX entity
ON :__Entity__(embedding)
WITH CONFIG {
    "dimension": 1024,
    "capacity": 2048,
    "metric": "cos",
    "scalar_kind": "f32"
};