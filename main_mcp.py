# main_mcp.py
import json

import json, time, sys, gc

def clear_memory():
    gc.collect()

if "/my_modules" not in sys.path:
    sys.path.insert(0, "/main")

from network_iot import Network
from mcp_factory import MCPFactory
from tools import suma, resta, multiplicacion, functions_list_data

# Configuración de la red
ssid = "SSID"
password = "PASSWORD"
# Configuración de IP estática (opcional)
static_ip_config = None
net = Network(ssid, password, static_ip_config)
if not net.conectar():
    print("Error al conectar la red. Saliendo...")
    raise SystemExit

# API Keys - Reemplaza con tus propias API keys
OPENAI_API_KEY = "OPENAI_API_KEY"
CLAUDE_API_KEY = "CLAUDE_API_KEY"
GEMINI_API_KEY = "GEMINI_API_KEY"

def procesar_resultado(respuesta, modelo_nombre, adapter):
    """
    Procesa el resultado de una consulta a un LLM.
    
    Args:
        respuesta (dict): Respuesta estandarizada del adaptador MCP
        modelo_nombre (str): Nombre del modelo para los mensajes
        adapter: Instancia del adaptador MCP usado
    
    Returns:
        Resultado de la operación si es llamada a función, o la respuesta de texto
    """
    if respuesta and respuesta.get("type") == "function_call":
        # Parsear la llamada a la función
        fn_name = respuesta["name"]
        try:
            args = json.loads(respuesta["arguments"])
        except:
            # Si ya es un diccionario
            if isinstance(respuesta["arguments"], dict):
                args = respuesta["arguments"]
            else:
                args = {}
        
        print(f"El modelo {modelo_nombre} ha solicitado la función: {fn_name}")
        print(f"Con los argumentos: {args}")
        
        # Ejecutar la función solicitada
        result = None
        if fn_name == "suma":
            result = suma(args["a"], args["b"])
        elif fn_name == "resta":
            result = resta(args["a"], args["b"])
        elif fn_name == "multiplicacion":
            result = multiplicacion(args["a"], args["b"])
        else:
            result = "Función no reconocida."
            
        print("Resultado de la operación: ", result)
        
        # Agregar el resultado al historial
        mensaje_asistente = f"El resultado de la operación es: {result}"
        adapter.agregar_mensaje("assistant", mensaje_asistente)
        
        return result
    
    elif respuesta and respuesta.get("type") == "text":
        print(f"Respuesta de texto de {modelo_nombre}:")
        print(respuesta["content"])
        return respuesta["content"]
    
    else:
        print("No se pudo obtener una respuesta adecuada.")
        return None

def ejecutar_consulta(proveedor, api_key, consulta, modelo=None):
    """
    Ejecuta una consulta completa con un adaptador MCP creado por la fábrica.
    
    Args:
        proveedor (str): Nombre del proveedor ("openai", "claude", "gemini")
        api_key (str): Clave API del proveedor
        consulta (str): Consulta del usuario
        modelo (str): Modelo específico a usar (opcional)
    """
    print(f"\n--- USANDO {proveedor.upper()} ---")
    
    # Crear el adaptador usando la fábrica
    try:
        adapter = MCPFactory.create_adapter(
            provider=proveedor,
            api_key=api_key,
            modelo=modelo,
            max_tokens=100,
            temperatura=0.7
        )
    except ValueError as e:
        print(f"Error: {e}")
        return
    
    # Configurar mensajes
    adapter.agregar_mensaje("system", "Eres un asistente que ayuda con operaciones matemáticas básicas.")
    adapter.agregar_mensaje("user", consulta)
    
    # Realizar la consulta con functions
    respuesta = adapter.consultar(functions=functions_list_data, function_call="auto")
    
    if respuesta:
        result = procesar_resultado(respuesta, proveedor, adapter)
        
        # Si fue una function_call, obtener una respuesta final
        if respuesta.get("type") == "function_call":
            respuesta_final = adapter.consultar()
            if respuesta_final and respuesta_final.get("type") == "text":
                print(f"\nRespuesta final de {proveedor}:")
                print(respuesta_final["content"])

def main():
    """Función principal para probar los adaptadores MCP"""
    # Elegir la consulta
    consulta = "Quiero multiplicar 4 y "
    # consulta = "cuentame un chiste"
    
    print(f"consulta: {consulta}")
    
    # Probar con OpenAI
    ejecutar_consulta("openai", OPENAI_API_KEY, consulta)
    
    # Descomenta para probar con Claude
    ejecutar_consulta("claude", CLAUDE_API_KEY, consulta)
    
    # Descomenta para probar con Gemini
    ejecutar_consulta("gemini", GEMINI_API_KEY, consulta)
    
    # También puedes especificar modelos específicos:
    # ejecutar_consulta("claude", CLAUDE_API_KEY, consulta, "claude-3-7-sonnet-20250219")
    # ejecutar_consulta("gemini", GEMINI_API_KEY, consulta, "gemini-2.0-flash")

if __name__ == "__main__":
    main()