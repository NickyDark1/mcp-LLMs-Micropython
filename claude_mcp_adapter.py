# claude_mcp_adapter.py
import urequests
import json
from mcp_base import MCPAdapter

class ClaudeMCPAdapter(MCPAdapter):
    """Adaptador MCP para la API de Anthropic Claude"""
    
    def __init__(self, api_key, modelo="claude-3-sonnet-20240229", max_tokens=50, temperatura=0.7):
        """
        Inicializa el adaptador para Claude.
        
        Args:
            api_key (str): Clave API de Anthropic
            modelo (str): Modelo a utilizar (por defecto 'claude-3-sonnet-20240229')
            max_tokens (int): Número máximo de tokens en la respuesta
            temperatura (float): Nivel de aleatoriedad (0.0-1.0)
        """
        super().__init__(api_key, modelo, max_tokens, temperatura)
        self.url = "https://api.anthropic.com/v1/messages"
    
    def _realizar_peticion(self, functions, function_call):
        """
        Realiza la petición a la API de Claude.
        
        Args:
            functions (list): Funciones disponibles en formato OpenAI (estándar)
            function_call (str): Modo de llamada a funciones (ignorado por Claude)
            
        Returns:
            dict: Respuesta cruda de Claude o None si hay error
        """
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        
        # Construir la estructura de datos para Claude
        data = {
            "model": self.modelo,
            "messages": self.historial.copy(),
            "max_tokens": self.max_tokens
        }
        
        # Añadir temperatura si está especificada
        if self.temperatura is not None:
            data["temperature"] = self.temperatura
        
        # Añadir mensaje de sistema si existe
        if self.system:
            data["system"] = self.system
        
        # Convertir y añadir herramientas si existen
        if functions is not None:
            claude_tools = self._convertir_funciones(functions)
            data["tools"] = claude_tools
        
        try:
            print("Enviando consulta a Claude...")
            response = urequests.post(self.url, headers=headers, data=json.dumps(data).encode("utf-8"))
            
            if response.status_code == 200:
                result = response.json()
                response.close()
                return result
            else:
                print(f"Error: {response.status_code} - {response.text}")
                response.close()
                return None
        except Exception as e:
            print(f"Excepción: {e}")
            return None
    
    def _procesar_respuesta(self, response):
        """
        Procesa la respuesta de Claude y la convierte al formato estándar.
        
        Args:
            response (dict): Respuesta cruda de Claude
            
        Returns:
            dict: Respuesta procesada en formato estándar
        """
        content_blocks = response["content"]
        
        # Buscar si hay tool_use (function call) en la respuesta
        for block in content_blocks:
            if block.get("type") == "tool_use":
                tool_use = block["tool_use"]
                return {
                    "type": "function_call",
                    "name": tool_use["name"],
                    "arguments": json.dumps(tool_use["input"])
                }
        
        # Si no hay tool_use, es una respuesta de texto normal
        respuesta_assistant = ""
        for block in content_blocks:
            if block["type"] == "text":
                respuesta_assistant += block["text"]
        
        # Guardar en el historial
        self.agregar_mensaje("assistant", respuesta_assistant)
        
        return {
            "type": "text",
            "content": respuesta_assistant
        }
    
    def _convertir_funciones(self, functions):
        """
        Convierte las funciones del formato OpenAI al formato de Claude.
        
        Args:
            functions (list): Funciones en formato OpenAI (estándar)
            
        Returns:
            list: Funciones convertidas al formato de Claude
        """
        claude_tools = []
        
        for func in functions:
            # Crear la estructura básica de la herramienta
            claude_tool = {
                "name": func["name"],
                "description": func.get("description", ""),
                "input_schema": {
                    "type": "object",
                    "properties": {}
                }
            }
            
            # Copiar todas las propiedades
            if "parameters" in func and "properties" in func["parameters"]:
                claude_tool["input_schema"]["properties"] = func["parameters"]["properties"]
            
            # Copiar campos required solo si existen
            if "parameters" in func and "required" in func["parameters"]:
                claude_tool["input_schema"]["required"] = func["parameters"]["required"]
            
            claude_tools.append(claude_tool)
        
        return claude_tools