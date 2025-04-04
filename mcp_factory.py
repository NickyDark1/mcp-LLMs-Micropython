# mcp_factory.py
from openai_mcp_adapter import OpenAIMCPAdapter
from claude_mcp_adapter import ClaudeMCPAdapter
from gemini_mcp_adapter import GeminiMCPAdapter

class MCPFactory:
    """
    Fábrica para crear instancias de adaptadores MCP.
    Simplifica la creación de adaptadores para diferentes proveedores.
    """
    
    @staticmethod
    def create_adapter(provider, api_key, modelo=None, max_tokens=50, temperatura=0.7):
        """
        Crea un adaptador MCP basado en el proveedor especificado.
        
        Args:
            provider (str): Proveedor de LLM ("openai", "claude", "gemini")
            api_key (str): Clave API para el proveedor
            modelo (str): Identificador del modelo a utilizar (específico para cada proveedor)
            max_tokens (int): Número máximo de tokens en la respuesta
            temperatura (float): Nivel de aleatoriedad (0.0-1.0)
            
        Returns:
            MCPAdapter: Una instancia del adaptador apropiado
            
        Raises:
            ValueError: Si el proveedor no es compatible
        """
        provider = provider.lower()
        
        if provider == "openai":
            # Usar modelo predeterminado si no se especifica
            if modelo is None:
                modelo = "gpt-3.5-turbo"
            return OpenAIMCPAdapter(api_key, modelo, max_tokens, temperatura)
        
        elif provider == "claude":
            # Usar modelo predeterminado si no se especifica
            if modelo is None:
                modelo = "claude-3-7-sonnet-20250219"
            return ClaudeMCPAdapter(api_key, modelo, max_tokens, temperatura)
        
        elif provider == "gemini":
            # Usar modelo predeterminado si no se especifica
            if modelo is None:
                modelo = "gemini-2.0-flash"
            return GeminiMCPAdapter(api_key, modelo, max_tokens, temperatura)
        
        else:
            raise ValueError(f"Proveedor '{provider}' no compatible. Use 'openai', 'claude' o 'gemini'.")