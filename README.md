# Gemini Function Calling Demo

A simple demonstration of Google Gemini API's Function Calling capability using a weather example.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the demo:
```bash
python gemini_function_call_demo.py
```

## How It Works

The demo shows the complete function calling flow:

1. **Function Declaration** - Defines a `get_weather` function with its parameters
2. **User Query** - Sends natural language queries to Gemini
3. **Function Detection** - Gemini decides if it needs to call the function
4. **Function Execution** - Your code executes the actual function
5. **Final Response** - Gemini uses the results to generate a natural response

## Example Output

```
User Query: What's the weather like in Tokyo?

Gemini wants to call a function:
  Function: get_weather
  Arguments: {'location': 'Tokyo'}

Function executed, result:
  {
    "location": "Tokyo",
    "temperature": 28,
    "unit": "C",
    "condition": "Rainy",
    "humidity": 80
  }

Gemini's final response:
  The weather in Tokyo is currently rainy with a temperature of 28°C and 80% humidity.
```

## Key Components

- **Dummy Weather Function**: Simulates weather data for demo purposes
- **Function Declaration**: JSON schema that tells Gemini about available functions
- **Chat Flow**: Demonstrates the back-and-forth between your app and Gemini
