# Gemini Function Calling Demo

This repository contains three Python scripts demonstrating Google Gemini's function calling capabilities using the official `google-genai` SDK.

## Setup

### Install the required package

```bash
pip install --user google-genai
```

### Set your API key

Update the `API_KEY` variable in each script with your Gemini API key.

## Scripts Overview

### 1. `gemini_function_call_demo.py` - Basic Weather Demo

A simple demonstration of the complete function calling workflow with a weather API example.

**Features:**
- Defines a mock `get_weather()` function
- Creates function declarations for the model
- Handles single-turn function calling
- Shows how to send function results back to the model

**Run:**
```bash
python gemini_function_call_demo.py
```

**Example queries:**
- "What's the weather like in Tokyo?"
- "Can you tell me the temperature in New York in Fahrenheit?"
- "Compare the weather between London and Paris"

---

### 2. `gemini_advanced_demo.py` - Advanced Features

Demonstrates advanced function calling features including automatic execution and parallel calls.

**Features:**
- Automatic function calling (Python SDK feature)
- Parallel function calling (multiple functions at once)
- Compositional function calling (function chaining)
- Different function calling modes (AUTO, ANY, NONE)

**Run:**
```bash
python gemini_advanced_demo.py
```

---

### 3. `gemini_complete_demo.py` - Comprehensive Guide

A complete, step-by-step demonstration following the official documentation.

**Features:**

#### Example 1: Basic Function Calling (Smart Light Control)
- Manual step-by-step function calling process
- Set light brightness and color temperature
- Shows the complete request-response-execution-response cycle

#### Example 2: Automatic Function Calling
- SDK automatically executes Python functions
- Temperature lookup example
- Minimal boilerplate code

#### Example 3: Compositional Function Calling
- Chains multiple functions together
- Example: Check weather → Set thermostat based on weather
- Sequential function execution

#### Example 4: Function Calling Modes
- **AUTO mode**: Model decides whether to call functions
- **ANY mode**: Forces the model to call a function
- **NONE mode**: Disables function calling

**Run:**
```bash
python gemini_complete_demo.py
```

## Key Concepts

### Function Declaration Format

```python
function_declaration = {
    "name": "function_name",
    "description": "Clear description of what the function does",
    "parameters": {
        "type": "object",
        "properties": {
            "param_name": {
                "type": "string",  # or "integer", "boolean", "array"
                "description": "Parameter description",
                "enum": ["option1", "option2"]  # Optional: for fixed values
            }
        },
        "required": ["param_name"]
    }
}
```

### Basic Usage Pattern

```python
from google import genai
from google.genai import types

# 1. Initialize client
client = genai.Client(api_key="YOUR_API_KEY")

# 2. Create tools
tools = types.Tool(function_declarations=[function_declaration])
config = types.GenerateContentConfig(tools=[tools])

# 3. Send request
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Your prompt here",
    config=config
)

# 4. Check for function call
if response.candidates[0].content.parts[0].function_call:
    function_call = response.candidates[0].content.parts[0].function_call
    # Execute your function
    result = your_function(**function_call.args)

    # 5. Send result back to model
    # ... (see examples for complete code)
```

### Automatic Function Calling (Python Only)

The Python SDK can automatically execute functions:

```python
def my_function(param: str) -> dict:
    """Function with type hints and docstring."""
    return {"result": "value"}

config = types.GenerateContentConfig(
    tools=[my_function]  # Pass function directly
)

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Call my function",
    config=config
)
# SDK automatically executes the function and returns final response
print(response.text)
```

## Function Calling Modes

| Mode | Behavior |
|------|----------|
| `AUTO` (default) | Model decides whether to call functions or respond with text |
| `ANY` | Model must call a function (no text-only responses) |
| `NONE` | Disables function calling temporarily |
| `VALIDATED` | Model can call functions or respond with text, with schema validation |

## Best Practices

1. **Clear Descriptions**: Be specific in function and parameter descriptions
2. **Use Enums**: For parameters with fixed values, use `enum` instead of just describing them
3. **Strong Typing**: Use specific types (integer, string, boolean) to reduce errors
4. **Temperature**: Use low temperature (e.g., 0) for deterministic function calls
5. **Validation**: Validate function calls before executing them, especially for critical operations
6. **Error Handling**: Implement robust error handling in your functions
7. **Security**: Be cautious when calling external APIs; use proper authentication

## Supported Models

| Model | Function Calling | Parallel | Compositional |
|-------|-----------------|----------|---------------|
| Gemini 3 Pro | ✔️ | ✔️ | ✔️ |
| Gemini 3 Flash | ✔️ | ✔️ | ✔️ |
| Gemini 2.5 Pro | ✔️ | ✔️ | ✔️ |
| Gemini 2.5 Flash | ✔️ | ✔️ | ✔️ |
| Gemini 2.5 Flash-Lite | ✔️ | ✔️ | ✔️ |
| Gemini 2.0 Flash | ✔️ | ✔️ | ✔️ |

## Documentation

For complete documentation, visit:
- [Gemini Function Calling Guide](https://ai.google.dev/gemini-api/docs/function-calling)
- [Google GenAI Python SDK](https://googleapis.github.io/python-genai/)

## Troubleshooting

### Issue: `google.generativeai` deprecation warning

**Solution**: Use `from google import genai` instead of `import google.generativeai as genai`

### Issue: Model not found error

**Solution**: Use `gemini-2.5-flash` or `gemini-2.5-pro` instead of older model names

### Issue: Function not being called

**Solution**:
- Check function declaration descriptions are clear
- Try using `mode='ANY'` to force function calling
- Verify parameter types match the schema

## Changes from Old API

If you're migrating from `google.generativeai`:

| Old API | New API |
|---------|---------|
| `import google.generativeai as genai` | `from google import genai` |
| `genai.configure(api_key=key)` | `client = genai.Client(api_key=key)` |
| `model = genai.GenerativeModel()` | `client.models.generate_content()` |
| `gemini-1.5-flash` | `gemini-2.5-flash` |
| Dictionary-based function declarations | Same (dict format) |
| `genai.protos.Content()` | `types.Content()` |

## License

This is a demonstration project based on Google's official documentation.
