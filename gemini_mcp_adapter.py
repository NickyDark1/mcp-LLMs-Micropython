import urequests
import json
from mcp_base import MCPAdapter

class GeminiMCPAdapter(MCPAdapter):
    """Adaptador MCP para la API de Google Gemini"""
    
    def __init__(self, api_key, modelo="gemini-2.0-flash", max_tokens=50, temperatura=0.7):
        """
        Inicializa el adaptador para Gemini.
        
        Args:
            api_key (str): Clave API de Google
            modelo (str): Modelo a utilizar (por defecto 'gemini-2.0-flash')
            max_tokens (int): Número máximo de tokens en la respuesta
            temperatura (float): Nivel de aleatoriedad (0.0-1.0)
        """
        super().__init__(api_key, modelo, max_tokens, temperatura)
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
        # Almacenar la última respuesta recibida para depuración
        self.ultima_respuesta = None
    
    def agregar_mensaje(self, rol, contenido):
        """
        Sobrescribe el método para manejar la conversión de roles específica de Gemini.
        
        Args:
            rol (str): Rol del mensaje ('system', 'user', 'assistant')
            contenido (str): Contenido del mensaje
        """
        if rol == "system":
            self.system = contenido
        else:
            # Gemini usa "model" en lugar de "assistant"
            rol_gemini = "model" if rol == "assistant" else rol
            self.historial.append({"role": rol_gemini, "content": contenido})
    
    def _realizar_peticion(self, functions, function_call):
        """
        Realiza la petición a la API de Gemini.
        
        Args:
            functions (list): Funciones disponibles en formato OpenAI (estándar)
            function_call (str): Modo de llamada a funciones
            
        Returns:
            dict: Respuesta cruda de Gemini o None si hay error
        """
        # URL con la API key
        url = f"{self.base_url}/models/{self.modelo}:generateContent?key={self.api_key}"
        
        # Transformar historial para el formato Gemini
        contents = []
        
        # Agregar mensaje del sistema si existe
        if self.system:
            contents.append({
                "role": "user",
                "parts": [{"text": f"system: {self.system}"}]
            })
        
        # Agregar el resto de mensajes
        for msg in self.historial:
            contents.append({
                "role": msg["role"],
                "parts": [{"text": msg["content"]}]
            })
        
        # Imprimir el historial para depuración
        #print(f"Historial a enviar: {json.dumps(contents)}")
        
        data = {
            "contents": contents,
            "generationConfig": {
                "temperature": self.temperatura,
                "maxOutputTokens": self.max_tokens,
                "topP": 0.95,
                "topK": 40
            }
        }
        
        # Agregar funciones si existen
        if functions is not None:
            # Convertir el formato de OpenAI a Gemini
            gemini_functions = self._convertir_funciones(functions)
            data["tools"] = [{
                "functionDeclarations": gemini_functions
            }]
            
            # En Gemini 2.0+, el modo auto es predeterminado
            if function_call != "auto":
                data["toolConfig"] = {
                    "functionCallingConfig": {
                        "mode": function_call
                    }
                }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        try:
            print("Enviando consulta a Gemini...")
            response = urequests.post(url, headers=headers, data=json.dumps(data).encode("utf-8"))
            
            if response.status_code == 200:
                result = response.json()
                # Guardar la respuesta para depuración
                self.ultima_respuesta = result
                #print(f"Respuesta de Gemini: {json.dumps(result)}")
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
        Procesa la respuesta de Gemini y la convierte al formato estándar.
        
        Args:
            response (dict): Respuesta cruda de Gemini
            
        Returns:
            dict: Respuesta procesada en formato estándar
        """
        # Verificar si hay candidatos en la respuesta
        if "candidates" in response and response["candidates"]:
            candidate = response["candidates"][0]
            
            # Extraer llamada a función si existe
            function_call_data = self._extraer_function_call(candidate)
            if function_call_data:
                return {
                    "type": "function_call",
                    "name": function_call_data["name"],
                    "arguments": function_call_data["arguments"]
                }
            
            # Es una respuesta de texto normal
            respuesta_text = None
            
            # Comprobar que content existe
            if "content" in candidate:
                content = candidate["content"]
                
                # Caso 1: Solo contiene "role": "model" (respuesta vacía)
                if len(content) == 1 and "role" in content and content["role"] == "model":
                    respuesta_text = "El modelo reconoció el resultado de la operación."
                
                # Caso 2: Estructura normal con parts
                elif "parts" in content:
                    respuesta_text = ""
                    for part in content["parts"]:
                        if "text" in part:
                            respuesta_text += part["text"]
                
                # Caso 3: Texto directo
                elif "text" in content:
                    respuesta_text = content["text"]
                
                # Caso 4: No se puede determinar, mostrar contenido para depuración
                if respuesta_text is None:
                    try:
                        respuesta_text = "Contenido sin formato estándar: " + json.dumps(content)
                    except:
                        respuesta_text = "Contenido no analizable"
            else:
                # Sin content, intentar leer directamente 
                if "text" in candidate:
                    respuesta_text = candidate["text"]
                else:
                    try:
                        respuesta_text = "Respuesta sin estructura content: " + json.dumps(candidate)
                    except:
                        respuesta_text = "Respuesta no analizable"
            
            # Si todavía no tenemos texto, usar un mensaje predeterminado
            if not respuesta_text:
                respuesta_text = "Recibido mensaje vacío del modelo tras procesar la operación."
            
            # Guardar en el historial (convertir de "model" a "assistant" para el estándar MCP)
            self.historial.append({"role": "assistant", "content": respuesta_text})
            
            return {
                "type": "text",
                "content": respuesta_text
            }
        else:
            print("No se encontraron candidatos en la respuesta")
            # Intentamos devolver información sobre lo que recibimos para depuración
            try:
                debug_info = "Respuesta sin candidatos: " + json.dumps(response)
                return {
                    "type": "text",
                    "content": debug_info
                }
            except:
                return None
    
    def _extraer_function_call(self, candidate):
        """
        Extrae la información de llamada a función de la respuesta de Gemini.
        
        Args:
            candidate (dict): Candidato de respuesta de Gemini
            
        Returns:
            dict: Información de la llamada a función o None
        """
        try:
            # Buscar en parts[].functionCall (formato en Gemini 2.0)
            if "content" in candidate and "parts" in candidate["content"]:
                for part in candidate["content"]["parts"]:
                    if "functionCall" in part:
                        return {
                            "name": part["functionCall"]["name"],
                            "arguments": json.dumps(part["functionCall"]["args"])
                        }
            
            # Buscar en functionCalls[] (formato alternativo)
            if "content" in candidate and "functionCalls" in candidate["content"]:
                function_call = candidate["content"]["functionCalls"][0]
                return {
                    "name": function_call["name"],
                    "arguments": json.dumps(function_call["args"])
                }
                
            # Buscar directamente en el candidato por si la estructura es diferente
            if "functionCall" in candidate:
                return {
                    "name": candidate["functionCall"]["name"],
                    "arguments": json.dumps(candidate["functionCall"]["args"])
                }
                
            # Otra estructura alternativa
            if "functionCalls" in candidate:
                function_call = candidate["functionCalls"][0]
                return {
                    "name": function_call["name"],
                    "arguments": json.dumps(function_call["args"])
                }
        except Exception as e:
            print(f"Error al extraer function call: {e}")
            return None
            
        return None
    
    def _convertir_funciones(self, functions):
        """
        Convierte las funciones del formato OpenAI al formato de Gemini.
        
        Args:
            functions (list): Funciones en formato OpenAI (estándar)
            
        Returns:
            list: Funciones convertidas al formato de Gemini
        """
        gemini_functions = []
        
        for func in functions:
            gemini_function = {
                "name": func["name"],
                "description": func.get("description", "")
            }
            
            # Convertir parámetros
            if "parameters" in func:
                params = {
                    "type": "object",  # Gemini usa "object" en minúsculas
                    "properties": {}
                }
                
                # Convertir propiedades
                if "properties" in func["parameters"]:
                    for prop_name, prop_details in func["parameters"]["properties"].items():
                        params["properties"][prop_name] = {
                            "type": prop_details["type"].lower(),  # Gemini usa tipos en minúsculas
                            "description": prop_details.get("description", "")
                        }
                        
                        # Manejar arrays y objetos anidados
                        if prop_details["type"].lower() == "array" and "items" in prop_details:
                            params["properties"][prop_name]["items"] = prop_details["items"]
                
                # Agregar campos required
                if "required" in func["parameters"]:
                    params["required"] = func["parameters"]["required"]
                
                gemini_function["parameters"] = params
            
            gemini_functions.append(gemini_function)
        
        return gemini_functions