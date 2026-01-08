"""
Gemini Complete Function Calling Demo
A comprehensive demonstration following the official documentation step-by-step
Based on: https://ai.google.dev/gemini-api/docs/function-calling
"""

from google import genai
from google.genai import types
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure the API key from environment variable
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("GEMINI_API_KEY not found. Please set it in .env file.")
client = genai.Client(api_key=API_KEY)


# ============================================================
# EXAMPLE 1: Basic Function Calling (Manual Execution)
# Following the official "How function calling works" guide
# ============================================================

print("\n" + "="*70)
print("EXAMPLE 1: BASIC FUNCTION CALLING - SMART LIGHT CONTROL")
print("="*70)

# Step 1: Define a function and its declaration
def set_light_values(brightness: int, color_temp: str) -> dict:
    """Set the brightness and color temperature of a room light. (mock API).

    Args:
        brightness: Light level from 0 to 100. Zero is off and 100 is full brightness
        color_temp: Color temperature of the light fixture

    Returns:
        A dictionary containing the set brightness and color temperature.
    """
    return {"brightness": brightness, "colorTemperature": color_temp}


set_light_values_declaration = {
    "name": "set_light_values",
    "description": "Sets the brightness and color temperature of a light.",
    "parameters": {
        "type": "object",
        "properties": {
            "brightness": {
                "type": "integer",
                "description": "Light level from 0 to 100. Zero is off and 100 is full brightness",
            },
            "color_temp": {
                "type": "string",
                "enum": ["daylight", "cool", "warm"],
                "description": "Color temperature of the light fixture, which can be `daylight`, `cool` or `warm`.",
            },
        },
        "required": ["brightness", "color_temp"],
    },
}

# Step 2: Configure the client and tools
tools = types.Tool(function_declarations=[set_light_values_declaration])
config = types.GenerateContentConfig(tools=[tools])

# Define user prompt
contents = [
    types.Content(
        role="user",
        parts=[types.Part(text="Turn the lights down to a romantic level")]
    )
]

# Step 3: Send request with function declarations
print("\nUser: Turn the lights down to a romantic level\n")

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=contents,
    config=config,
)

# Step 4: Check for function call
function_call = response.candidates[0].content.parts[0].function_call
if function_call:
    print(f"Model wants to call function: {function_call.name}")
    print(f"With arguments: {dict(function_call.args)}\n")

    # Step 5: Execute the function
    result = set_light_values(**function_call.args)
    print(f"Function execution result: {result}\n")

    # Step 6: Create function response and send back to model
    function_response_part = types.Part.from_function_response(
        name=function_call.name,
        response={"result": result},
    )

    # Append function call and result
    contents.append(response.candidates[0].content)
    contents.append(types.Content(role="user", parts=[function_response_part]))

    # Step 7: Get final response
    final_response = client.models.generate_content(
        model="gemini-2.5-flash",
        config=config,
        contents=contents,
    )

    print(f"Model's final response: {final_response.text}")


# ============================================================
# EXAMPLE 2: Automatic Function Calling (Python SDK Feature)
# SDK handles function execution automatically
# ============================================================

print("\n" + "="*70)
print("EXAMPLE 2: AUTOMATIC FUNCTION CALLING")
print("="*70)

def get_current_temperature(location: str) -> dict:
    """Gets the current temperature for a given location.

    Args:
        location: The city and state, e.g. San Francisco, CA

    Returns:
        A dictionary containing the temperature and unit.
    """
    # Mock temperature data
    temperatures = {
        "San Francisco, CA": 18,
        "Boston, MA": 15,
        "New York, NY": 22,
        "London, UK": 12,
        "Paris, France": 20
    }
    temp = temperatures.get(location, 20)
    print(f"  [Function Called: get_current_temperature(location='{location}')]")
    print(f"  [Function Result: {temp}°C]\n")
    return {"temperature": temp, "unit": "Celsius"}


# Configure with Python function directly
config_auto = types.GenerateContentConfig(
    tools=[get_current_temperature]
)

print("\nUser: What's the temperature in Boston, MA?")
print()

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="What's the temperature in Boston, MA?",
    config=config_auto
)

print(f"Model's response: {response.text}")


# ============================================================
# EXAMPLE 3: Compositional Function Calling
# Chaining multiple function calls together
# ============================================================

print("\n" + "="*70)
print("EXAMPLE 3: COMPOSITIONAL FUNCTION CALLING")
print("="*70)

def get_weather_forecast(location: str) -> dict:
    """Gets the current weather temperature for a given location."""
    temperatures = {
        "London": 25,
        "Paris": 18,
        "New York": 22,
        "Tokyo": 28
    }
    temp = temperatures.get(location, 20)
    result = {"temperature": temp, "unit": "celsius"}
    print(f"  [Function Called: get_weather_forecast(location='{location}')]")
    print(f"  [Function Result: {result}]")
    return result


def set_thermostat_temperature(temperature: int) -> dict:
    """Sets the thermostat to a desired temperature."""
    result = {"status": "success", "set_to": temperature}
    print(f"  [Function Called: set_thermostat_temperature(temperature={temperature})]")
    print(f"  [Function Result: {result}]\n")
    return result


config_comp = types.GenerateContentConfig(
    tools=[get_weather_forecast, set_thermostat_temperature]
)

print("\nUser: If it's warmer than 20°C in London, set the thermostat to 20°C, otherwise set it to 18°C.")
print()

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="If it's warmer than 20°C in London, set the thermostat to 20°C, otherwise set it to 18°C.",
    config=config_comp
)

print(f"Model's response: {response.text}")


# ============================================================
# EXAMPLE 4: Function Calling Modes
# ============================================================

print("\n" + "="*70)
print("EXAMPLE 4: FUNCTION CALLING MODES")
print("="*70)

def calculate_sum(a: float, b: float) -> dict:
    """Calculates the sum of two numbers."""
    result = a + b
    print(f"  [Function Called: calculate_sum(a={a}, b={b})]")
    print(f"  [Function Result: {result}]\n")
    return {"result": result}


# Mode: AUTO (default) - Model decides
print("\n--- Mode: AUTO (Model decides whether to call function) ---")
print("User: What is 25 + 37?")
print()

config_auto_mode = types.GenerateContentConfig(
    tools=[calculate_sum]
    # mode defaults to AUTO
)

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="What is 25 + 37?",
    config=config_auto_mode
)

print(f"Model's response: {response.text}")


# Mode: ANY - Forces function call
print("\n--- Mode: ANY (Forces model to call function) ---")
print("User: Hello, how are you?")
print()

config_any_mode = types.GenerateContentConfig(
    tools=[calculate_sum],
    tool_config=types.ToolConfig(
        function_calling_config=types.FunctionCallingConfig(mode='ANY')
    )
)

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Hello, how are you?",
    config=config_any_mode
)

# In ANY mode, the model is forced to call a function
if response.candidates[0].content.parts[0].function_call:
    fc = response.candidates[0].content.parts[0].function_call
    print(f"Model was forced to call: {fc.name}({dict(fc.args)})")
    print("(Note: This may not make sense given the prompt)")


print("\n" + "="*70)
print("ALL DEMOS COMPLETE")
print("="*70 + "\n")
