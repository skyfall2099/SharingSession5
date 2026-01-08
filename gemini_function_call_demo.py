"""
Gemini Function Calling Demo
A simple demonstration of how to use function calling with Google Gemini API
Based on official documentation: https://ai.google.dev/gemini-api/docs/function-calling
"""

from google import genai
from google.genai import types
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure the API key from environment variable
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("GEMINI_API_KEY not found. Please set it in .env file.")
client = genai.Client(api_key=API_KEY)


# Step 1: Define a dummy weather function
def get_weather(location: str, unit: str = "celsius") -> dict:
    """
    Dummy function that simulates getting weather data.
    In a real application, this would call an actual weather API.
    """
    # Simulate weather data for different locations
    weather_data = {
        "New York": {"temperature": 22, "condition": "Sunny", "humidity": 60},
        "London": {"temperature": 15, "condition": "Cloudy", "humidity": 75},
        "Tokyo": {"temperature": 28, "condition": "Rainy", "humidity": 80},
        "Paris": {"temperature": 18, "condition": "Partly Cloudy", "humidity": 65},
    }

    # Get weather for the location, or return default
    weather = weather_data.get(location, {"temperature": 20, "condition": "Unknown", "humidity": 50})

    # Convert to Fahrenheit if requested
    if unit.lower() == "fahrenheit":
        weather["temperature"] = round(weather["temperature"] * 9/5 + 32, 1)
        weather["unit"] = "F"
    else:
        weather["unit"] = "C"

    return {
        "location": location,
        "temperature": weather["temperature"],
        "unit": weather["unit"],
        "condition": weather["condition"],
        "humidity": weather["humidity"]
    }


# Step 2: Define the function declaration for Gemini
# This tells Gemini what functions are available and how to call them
get_weather_declaration = {
    "name": "get_weather",
    "description": "Get the current weather for a specific location",
    "parameters": {
        "type": "object",
        "properties": {
            "location": {
                "type": "string",
                "description": "The city name, e.g., New York, London, Tokyo"
            },
            "unit": {
                "type": "string",
                "description": "Temperature unit: celsius or fahrenheit",
                "enum": ["celsius", "fahrenheit"]
            }
        },
        "required": ["location"]
    }
}

# Step 3: Create tools with function declarations
weather_tool = types.Tool(function_declarations=[get_weather_declaration])


def demo_function_calling(user_query: str):
    """
    Demonstrates the complete function calling flow following official documentation.
    Supports parallel function calling (multiple functions called at once).
    """
    print(f"\n{'='*60}")
    print(f"User Query: {user_query}")
    print(f"{'='*60}\n")

    # Step 4: Send the initial request to Gemini with tools
    config = types.GenerateContentConfig(tools=[weather_tool])

    contents = [
        types.Content(
            role="user",
            parts=[types.Part(text=user_query)]
        )
    ]

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=contents,
        config=config
    )

    # Step 5: Check ALL parts for function calls (supports parallel calling)
    function_calls = [
        part.function_call
        for part in response.candidates[0].content.parts
        if part.function_call
    ]

    if function_calls:
        print(f"Gemini wants to call {len(function_calls)} function(s):\n")

        # Step 6: Execute ALL function calls and collect results
        function_response_parts = []
        for i, function_call in enumerate(function_calls, 1):
            print(f"  [{i}] Function: {function_call.name}")
            print(f"      Arguments: {dict(function_call.args)}")

            if function_call.name == "get_weather":
                args = dict(function_call.args)
                weather_result = get_weather(**args)
                print(f"      Result: {json.dumps(weather_result)}\n")

                # Step 7: Create function response part for each call
                function_response_parts.append(
                    types.Part.from_function_response(
                        name=function_call.name,
                        response={"result": weather_result}
                    )
                )

        # Step 8: Append model's response and ALL function results to contents
        contents.append(response.candidates[0].content)  # Model's response with function calls
        contents.append(types.Content(role="user", parts=function_response_parts))  # All function results

        print(f"[DEBUG] Contents before final request (第二次请求前的内容):")
        print(f"Length of contents: {len(contents)}")
        for idx, content in enumerate(contents):
            print(f"\n  [{idx}] Role: {content.role}")
            print(f"       Number of Parts: {len(content.parts)}")
            for part_idx, part in enumerate(content.parts):
                print(f"         Part[{part_idx}]: {type(part).__name__}")
                if hasattr(part, 'text') and part.text:
                    text_preview = part.text[:100] + "..." if len(part.text) > 100 else part.text
                    print(f"                Text: {text_preview}")
                if hasattr(part, 'function_call') and part.function_call:
                    print(f"                Function Call: {part.function_call.name}({dict(part.function_call.args)})")
                if hasattr(part, 'function_response') and part.function_response:
                    print(f"                Function Response: {part.function_response}")
        print()

        # Step 9: Send all function results back to get final response
        final_response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=contents,
            config=config
        )

        print("Gemini's final response:")
        print(f"  {final_response.text}\n")
    else:
        # If no function call was needed, just show the direct response
        print("No function call needed. Direct response:")
        print(f"  {response.text}\n")


if __name__ == "__main__":
    # Run several demo queries
    print("\n" + "="*60)
    print("GEMINI FUNCTION CALLING DEMO")
    print("="*60)

    # Example 1: Simple weather query
    demo_function_calling("What's the weather like in Tokyo?")

    # Example 2: Weather with specific unit
    demo_function_calling("Can you tell me the temperature in New York in Fahrenheit?")

    # Example 3: Multiple locations
    demo_function_calling("London, Paris or Tokyo, where is the warmest?")

    print("\n" + "="*60)
    print("DEMO COMPLETE")
    print("="*60 + "\n")
