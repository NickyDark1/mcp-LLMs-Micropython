# MCP Micropython - Message Chat Protocol for LLMs 


![MCP Banner](https://github.com/user-attachments/assets/9ae557a6-e2dc-4e7a-94a5-7dd0fcf12377)



## Description

MCP (Message Chat Protocol) is a MicroPython library that provides a standard and unified interface for interacting with different Large Language Model (LLM) APIs. It allows you to use OpenAI, Claude, and Gemini with a consistent interface, simplifying the process of switching between different providers.

## Features

- **Unified Interface**: Same usage pattern for all LLM providers
- **Factory Pattern**: Easy creation of adapters through a factory
- **Function Calling**: Support for function calls across all models
- **MicroPython Compatible**: Specifically designed for resource-constrained environments
- **Robust Error Handling**: Adapted for the peculiarities of each API

## Requirements

- MicroPython 1.17 or higher
- Working Internet connection
- API keys for the providers you wish to use (OpenAI, Claude, and/or Gemini)

## Installation

1. Clone this repository:
```bash
git clone https://github.com/NickyDark1/mcp-LLMs-Micropython.git
```


2. Copy the files to your project directory or to your MicroPython device's filesystem.

3. Make sure your device has internet connectivity configured.

## Project Structure

```
mcp-protocol/
├── mcp_base.py            # Abstract base class for adapters
├── openai_mcp_adapter.py  # Adapter for OpenAI
├── claude_mcp_adapter.py  # Adapter for Claude (Anthropic)
├── gemini_mcp_adapter.py  # Adapter for Gemini (Google)
├── mcp_factory.py         # Factory for creating adapters
├── main_mcp.py            # Usage example
├── network_iot.py         # Utility for setting up internet connection
└── tools.py               # Example functions for function calling
```

## Basic Usage

```python
from mcp_factory import MCPFactory
from tools import functions_list_data

# Create an adapter for any provider using the Factory
adapter = MCPFactory.create_adapter(
    provider="openai",  # Can be "openai", "claude", or "gemini"
    api_key="your-api-key-here",
    modelo="gpt-3.5-turbo",  # Optional, each provider has defaults
    max_tokens=50,
    temperatura=0.7
)

# Add messages to the conversation history
adapter.agregar_mensaje("system", "You are an assistant that helps with math operations.")
adapter.agregar_mensaje("user", "I want to multiply 4 and 5")

# Make a query with function calling
respuesta = adapter.consultar(functions=functions_list_data, function_call="auto")

# Process the response
if respuesta["type"] == "function_call":
    # Handle function call
    funcion = respuesta["name"]
    argumentos = json.loads(respuesta["arguments"])
    print(f"Function call: {funcion}({argumentos})")
    
    # You can execute the function and add the result to the history
    resultado = ejecutar_funcion(funcion, argumentos)
    adapter.agregar_mensaje("assistant", f"The result is: {resultado}")
    
    # Continue the conversation
    respuesta_final = adapter.consultar()
    print(respuesta_final["content"])
else:
    # It's a normal text response
    print(respuesta["content"])
```

## Examples

### Complete Usage Example

Check the `main_mcp.py` file for a complete example of how to use the adapters with all three providers and process the responses.

### Switching Between Providers

```python
# Use OpenAI
openai_adapter = MCPFactory.create_adapter("openai", OPENAI_API_KEY)
openai_adapter.agregar_mensaje("user", "Hello, can you help me with math?")
respuesta = openai_adapter.consultar()

# Use Claude
claude_adapter = MCPFactory.create_adapter("claude", CLAUDE_API_KEY)
claude_adapter.agregar_mensaje("user", "Hello, can you help me with math?")
respuesta = claude_adapter.consultar()

# Use Gemini
gemini_adapter = MCPFactory.create_adapter("gemini", GEMINI_API_KEY)
gemini_adapter.agregar_mensaje("user", "Hello, can you help me with math?")
respuesta = gemini_adapter.consultar()
```

### Specifying Specific Models

```python
# OpenAI with GPT-4
adapter = MCPFactory.create_adapter("openai", OPENAI_API_KEY, "gpt-4")

# Claude with the latest model
adapter = MCPFactory.create_adapter("claude", CLAUDE_API_KEY, "claude-3-7-sonnet-20250219")

# Gemini with specific model
adapter = MCPFactory.create_adapter("gemini", GEMINI_API_KEY, "gemini-2.0-flash")
```

## Customization

You can extend MCP to support other LLM providers by creating new adapters:

1. Create a new class that inherits from `MCPAdapter`
2. Implement the required methods (`_realizar_peticion`, `_procesar_respuesta`, `_convertir_funciones`)
3. Add your adapter to the factory in `mcp_factory.py`

## Donations

If you find this project useful, please consider making a donation to support its development:

**Ethereum (ETH):** `0x691C9bbcA4Cc3335bdb21396817ed35b36f7cC0b`

Your support is greatly appreciated and helps us continue improving the project.

---

Developed with ❤️ for the MicroPython community
