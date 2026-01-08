"""
Gemini Advanced Function Calling Demo
Demonstrates parallel function calling and automatic function calling features
Based on official documentation: https://ai.google.dev/gemini-api/docs/function-calling
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
# EXAMPLE 1: Automatic Function Calling (Python SDK Feature)
# ============================================================

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
        "London, UK": 12
    }
    temp = temperatures.get(location, 20)
    return {"temperature": temp, "unit": "Celsius"}


def demo_automatic_function_calling():
    """
    Demonstrates automatic function calling where the SDK handles
    the function execution automatically
    """
    print("\n" + "="*60)
    print("EXAMPLE 1: AUTOMATIC FUNCTION CALLING")
    print("="*60 + "\n")

    # Configure with Python function directly (SDK converts it automatically)
    config = types.GenerateContentConfig(
        tools=[get_current_temperature]  # Pass the function itself
    )

    # Make the request
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents="What's the temperature in Boston?",
        config=config
    )

    print("User Query: What's the temperature in Boston?")
    print(f"Final Response: {response.text}\n")


# ============================================================
# EXAMPLE 2: Parallel Function Calling
# ============================================================

def power_disco_ball(power: bool) -> dict:
    """Powers the spinning disco ball."""
    return {"status": f"Disco ball powered {'on' if power else 'off'}"}


def start_music(energetic: bool, loud: bool) -> dict:
    """Play some music matching the specified parameters."""
    music_type = "energetic" if energetic else "chill"
    volume = "loud" if loud else "quiet"
    return {"music_type": music_type, "volume": volume}


def dim_lights(brightness: float) -> dict:
    """Dim the lights."""
    return {"brightness": brightness}


def demo_parallel_function_calling():
    """
    Demonstrates parallel function calling where multiple functions
    are called at once
    """
    print("\n" + "="*60)
    print("EXAMPLE 2: PARALLEL FUNCTION CALLING")
    print("="*60 + "\n")

    # Configure with Python functions
    config = types.GenerateContentConfig(
        tools=[power_disco_ball, start_music, dim_lights],
        # Force the model to call functions instead of chatting
        tool_config=types.ToolConfig(
            function_calling_config=types.FunctionCallingConfig(mode='ANY')
        )
    )

    # Make the request
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents="Turn this place into a party!",
        config=config
    )

    print("User Query: Turn this place into a party!")
    print("Model called multiple functions in parallel:\n")

    # The SDK automatically executes all function calls
    print(f"Final Response: {response.text}\n")


# ============================================================
# EXAMPLE 3: Compositional Function Calling
# ============================================================

def get_weather_forecast(location: str) -> dict:
    """Gets the current weather temperature for a given location."""
    print(f"  Tool Call: get_weather_forecast(location={location})")
    # Mock weather data
    temperatures = {
        "London": 25,
        "Paris": 18,
        "New York": 22
    }
    temp = temperatures.get(location, 20)
    result = {"temperature": temp, "unit": "celsius"}
    print(f"  Tool Response: {result}")
    return result


def set_thermostat_temperature(temperature: int) -> dict:
    """Sets the thermostat to a desired temperature."""
    print(f"  Tool Call: set_thermostat_temperature(temperature={temperature})")
    result = {"status": "success"}
    print(f"  Tool Response: {result}")
    return result


def demo_compositional_function_calling():
    """
    Demonstrates compositional function calling where functions are
    called in sequence to fulfill a complex request
    """
    print("\n" + "="*60)
    print("EXAMPLE 3: COMPOSITIONAL FUNCTION CALLING")
    print("="*60 + "\n")

    # Configure the client and model
    config = types.GenerateContentConfig(
        tools=[get_weather_forecast, set_thermostat_temperature]
    )

    print("User Query: If it's warmer than 20°C in London, set the thermostat to 20°C, otherwise set it to 18°C.")
    print("\nFunction calls executed:\n")

    # Make the request
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents="If it's warmer than 20°C in London, set the thermostat to 20°C, otherwise set it to 18°C.",
        config=config
    )

    print(f"\nFinal Response: {response.text}\n")


# ============================================================
# EXAMPLE 4: Function Calling Modes
# ============================================================

def get_stock_price(symbol: str) -> dict:
    """Gets the current stock price for a given symbol."""
    # Mock stock prices
    prices = {
        "AAPL": 175.50,
        "GOOGL": 140.25,
        "MSFT": 380.00
    }
    return {"symbol": symbol, "price": prices.get(symbol, 100.0)}


def demo_function_calling_modes():
    """
    Demonstrates different function calling modes (AUTO, ANY, NONE)
    """
    print("\n" + "="*60)
    print("EXAMPLE 4: FUNCTION CALLING MODES")
    print("="*60 + "\n")

    # Mode: ANY - Forces the model to call a function
    print("Mode: ANY (Forces function call)")
    config_any = types.GenerateContentConfig(
        tools=[get_stock_price],
        tool_config=types.ToolConfig(
            function_calling_config=types.FunctionCallingConfig(
                mode='ANY',
                allowed_function_names=["get_stock_price"]
            )
        )
    )

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents="Hello, how are you?",  # Not a stock-related query
        config=config_any
    )
    print(f"Response: {response.text}\n")

    # Mode: AUTO (default) - Model decides whether to call function
    print("Mode: AUTO (Model decides)")
    config_auto = types.GenerateContentConfig(
        tools=[get_stock_price]
    )

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents="Hello, how are you?",
        config=config_auto
    )
    print(f"Response: {response.text}\n")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("GEMINI ADVANCED FUNCTION CALLING DEMOS")
    print("="*60)

    # Run all demos
    demo_automatic_function_calling()
    demo_parallel_function_calling()
    demo_compositional_function_calling()
    demo_function_calling_modes()

    print("\n" + "="*60)
    print("ALL DEMOS COMPLETE")
    print("="*60 + "\n")
