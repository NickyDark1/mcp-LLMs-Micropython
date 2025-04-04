# my_functions.py
def suma(a, b):
    """
    hola mundo
    """
    return a + b

def resta(a, b):
    return a - b

def multiplicacion(a, b):
    return a * b


FUNCTION_META = {
    "suma": {
        "description": "Esta función suma dos valores a y b.",
        "args": {
            "a": {"type": "number", "description": "Primer sumando"},
            "b": {"type": "number", "description": "Segundo sumando"}
        },
        "required": ["a", "b"]
    },
    "resta": {
        "description": "Resta b de a.",
        "args": {
            "a": {"type": "number", "description": "Minuendo"},
            "b": {"type": "number", "description": "Sustraendo"}
        },
        "required": ["a", "b"]
    },
    "multiplicacion": {
        "description": "Multiplica a y b.",
        "args": {
            "a": {"type": "number", "description": "Primer factor"},
            "b": {"type": "number", "description": "Segundo factor"}
        },
        "required": ["a", "b"]
    }
}


def build_schema_from_metadata(func_name, meta):
    return {
        "name": func_name,
        "description": meta["description"],
        "parameters": {
            "type": "object",
            "properties": meta["args"],
            "required": meta["required"]
        }
    }

def build_functions_list():
    functions_list = []
    for fname, meta in FUNCTION_META.items():
        schema = build_schema_from_metadata(fname, meta)
        functions_list.append(schema)
    return functions_list

functions_list_data = build_functions_list()
# Ahora functions_list se ve como
# [
#   {
#     "name": "suma",
#     "description": "...",
#     "parameters": {
#       "type": "object",
#       "properties": {...},
#       "required": [...]
#     }
#   },
#   ...
# ]

#print(functions_list)
