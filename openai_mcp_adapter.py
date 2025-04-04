# openai_mcp_adapter.py
import urequests
import json
from mcp_base import MCPAdapter

class OpenAIMCPAdapter(MCPAdapter):
    """Adaptador MCP para la API de OpenAI"""
    
    def __init__(self, api_key, modelo="gpt-3.5-turbo", max_tokens=50, temperatura=0.7):
        """
        Inicializa el adaptador para OpenAI.
        
        Args:
            api_key (str): Clave API de OpenAI
            modelo (str): Modelo a utilizar (por defecto 'gpt-3.5-turbo')
            max_tokens (int): Número máximo de tokens en la respuesta
            temperatura (float): Nivel de aleatoriedad (0.0-1.0)
        """
        super().__init__(api_key, modelo, max_tokens, temperatura)
        self.url = "https://api.openai.com/v1/chat/completions"
    
    def _realizar_peticion(self, functions, function_call):
        """
        Realiza la petición a la API de OpenAI.
        
        Args:
            functions (list): Funciones disponibles en formato OpenAI
            function_call (str): Modo de llamada a funciones
            
        Returns:
            dict: Respuesta cruda de OpenAI o None si hay error
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        # Preparar mensajes para OpenAI
        messages = []
        
        # Agregar mensaje de sistema si existe
        if self.system:
            messages.append({"role": "system", "content": self.system})
        
        # Agregar el resto de mensajes
        messages.extend(self.historial)
        
        data = {
            "model": self.modelo,
            "messages": messages,
            "temperature": self.temperatura,
            "max_tokens": self.max_tokens,
        }
        
        # Agregar funciones si existen
        if functions is not None:
            data["functions"] = functions
            data["function_call"] = function_call
        
        try:
            print("Enviando consulta a OpenAI...")
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
        Procesa la respuesta de OpenAI y la convierte al formato estándar.
        
        Args:
            response (dict): Respuesta cruda de OpenAI
            
        Returns:
            dict: Respuesta procesada en formato estándar
        """
        mensaje_obj = response["choices"][0]["message"]
        
        # Verificar si es una llamada a función
        if "function_call" in mensaje_obj:
            return {
                "type": "function_call",
                "name": mensaje_obj["function_call"]["name"],
                "arguments": mensaje_obj["function_call"]["arguments"]
            }
        else:
            # Es una respuesta de texto normal
            respuesta_assistant = mensaje_obj["content"]
            
            # Guardar en el historial
            self.agregar_mensaje("assistant", respuesta_assistant)
            
            return {
                "type": "text",
                "content": respuesta_assistant
            }
    
    def _convertir_funciones(self, functions):
        """
        Convierte las funciones al formato de OpenAI (que es el formato estándar).
        En este caso, no se requiere conversión ya que OpenAI es la referencia.
        
        Args:
            functions (list): Funciones en formato OpenAI
            
        Returns:
            list: Las mismas funciones sin modificar
        """
        return functions