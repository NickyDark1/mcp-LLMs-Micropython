# mcp_base.py
import json

class MCPAdapter:
    """
    Clase base para adaptadores de Message Chat Protocol (MCP).
    Define la interfaz común que todos los adaptadores deben implementar.
    """
    
    def __init__(self, api_key, modelo, max_tokens=50, temperatura=0.7):
        """
        Inicializa el adaptador MCP con configuraciones comunes.
        
        Args:
            api_key (str): Clave API para el servicio de LLM
            modelo (str): Identificador del modelo a utilizar
            max_tokens (int): Número máximo de tokens en la respuesta
            temperatura (float): Nivel de aleatoriedad en las respuestas (0.0-1.0)
        """
        self.api_key = api_key
        self.modelo = modelo
        self.max_tokens = max_tokens
        self.temperatura = temperatura
        self.historial = []
        self.system = ""
    
    def agregar_mensaje(self, rol, contenido):
        """
        Agrega un mensaje al historial de conversación.
        
        Args:
            rol (str): Rol del mensaje ('system', 'user', 'assistant')
            contenido (str): Contenido del mensaje
        """
        if rol == "system":
            self.system = contenido
        else:
            self.historial.append({"role": rol, "content": contenido})
    
    def consultar(self, nuevos_mensajes=None, functions=None, function_call="auto"):
        """
        Realiza una consulta al LLM y procesa la respuesta.
        
        Args:
            nuevos_mensajes (list): Lista opcional de mensajes a agregar al historial
            functions (list): Lista opcional de funciones disponibles para el modelo
            function_call (str): Modo de llamada a funciones ("auto", "none", o nombre específico)
            
        Returns:
            dict: Respuesta procesada con formato estandarizado
                 {"type": "text", "content": str} o
                 {"type": "function_call", "name": str, "arguments": str}
        """
        # Agregar nuevos mensajes al historial si existen
        if nuevos_mensajes:
            for mensaje in nuevos_mensajes:
                self.agregar_mensaje(mensaje["role"], mensaje["content"])
        
        # Realizar la petición al proveedor específico
        response = self._realizar_peticion(functions, function_call)
        
        # Si hubo un error en la petición
        if response is None:
            return None
        
        # Procesar y estandarizar la respuesta
        return self._procesar_respuesta(response)
    
    def _realizar_peticion(self, functions, function_call):
        """
        Método que debe ser implementado por cada adaptador específico.
        Realiza la petición al API del proveedor y retorna la respuesta cruda.
        
        Args:
            functions (list): Funciones disponibles
            function_call (str): Modo de llamada a funciones
            
        Returns:
            dict: Respuesta cruda del proveedor
        """
        raise NotImplementedError("Subclases deben implementar _realizar_peticion()")
    
    def _procesar_respuesta(self, response):
        """
        Método que debe ser implementado por cada adaptador específico.
        Procesa la respuesta cruda del proveedor y la convierte al formato estandarizado.
        
        Args:
            response (dict): Respuesta cruda del proveedor
            
        Returns:
            dict: Respuesta procesada con formato estandarizado
        """
        raise NotImplementedError("Subclases deben implementar _procesar_respuesta()")
    
    def _convertir_funciones(self, functions):
        """
        Método que debe ser implementado por cada adaptador específico.
        Convierte las funciones del formato estándar al formato específico del proveedor.
        
        Args:
            functions (list): Funciones en formato OpenAI (estándar)
            
        Returns:
            list/dict: Funciones convertidas al formato específico del proveedor
        """
        raise NotImplementedError("Subclases deben implementar _convertir_funciones()")