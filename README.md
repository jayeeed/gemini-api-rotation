# Gemini Rotate

![Async](https://img.shields.io/badge/async-supported-blue)
![Python](https://img.shields.io/badge/python-3.9+-green)

A lightweight **Async** Python library for Google Gemini API key rotation, valid model selection, and automatic fallback to "Lite" models on server errors.

## 🚀 Features

- **✅ Automatic Key Rotation**: Seamlessly rotates through a list of API keys when quota is exhausted (`429`), permission denied (`403`), or any other API error occurs.
- **🔄 Smart Model Fallback**: Automatically downgrades specific models (e.g., `gemini-2.0-flash` -> `gemini-2.0-flash-lite`) if server errors (`5xx`) persist.
- **⚡ Async First**: Built on top of the `google-genai` async client for high-performance non-blocking applications.
- **🛡️ Robust Error Handling**: Implements exponential backoff before rotating keys or switching models.
- **📝 Concise Logging**: Logs only essential success/failure information (e.g., `400 INVALID_ARGUMENT`) to keep your console clean.

## 📦 Installation
```bash
pip install gemini-rotate
```

## ⚡ Quick Start

1.  **Configure Environment**: Create a `.env` file.
    ```env
    GEMINI_API_KEY_1="AIzaSy..."
    GEMINI_API_KEY_2="AI3yhj..."
    GEMINI_API_KEY_3="AIdf56..."
    ```

2.  **Run Code**:
    ```python
    import asyncio
    from gemini_rotate import GeminiRotationClient
    
    async def main():
        client = GeminiRotationClient()
        response = await client.generate_content("Hello, Gemini!")
        print(response.text)
    
    asyncio.run(main())
    ```

## 📖 Usage Guide

### Initialization
The client automatically loads API keys from your environment variables (`GEMINI_API_KEY_1`, `GEMINI_API_KEY_2`, etc.).

```python
client = GeminiRotationClient()
```

### Generating Content
The `generate_content` method wraps the standard `google-genai` call but adds rotation and fallback logic.

#### 1. Basic Text Generation
```python
import asyncio
from gemini_rotate import GeminiRotationClient
from dotenv import load_dotenv

load_dotenv()

async def generate_text():
    client = GeminiRotationClient()
    try:
        response = await client.generate_content(
            contents="Explain quantum computing in 50 words."
        )
        print(f"Generated text: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(generate_text())
```

#### 2. Advanced: Tool Calling & Structured Output
You can pass `tools` and `response_schema` (or `response_mime_type`) via the `config` parameter.

```python
import asyncio
from google import genai
from gemini_rotate import GeminiRotationClient
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

# Define a schema for structured output
class Recipe(BaseModel):
    title: str
    ingredients: list[str]
    instructions: list[str]

async def generate_recipe():
    client = GeminiRotationClient()

    try:
        response = await client.generate_content(
            contents="Give me a recipe for chocolate cake.",
            config={
                "response_mime_type": "application/json",
                "response_schema": Recipe,
            }
        )
        
        # Parse result directly into Pydantic model
        recipe = response.parsed
        print(f"Title: {recipe.title}")
        print(f"Ingredients: {recipe.ingredients}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(generate_recipe())
```

#### Parameters
| Parameter | Type | Description |
| :--- | :--- | :--- |
| `contents` | `str` \| `list` | The prompt or content to send. |
| `model` | `str` | (Optional) The specific model to use. Defaults to first in priority list. |
| `config` | `dict` | (Optional) Generation config (temperature, tools, schema) passed to `google.genai`. |

## ⚙️ Configuration

### 1. API Keys (Required)
Define your keys in `.env` or environment variables using the pattern `GEMINI_API_KEY_n`.

```env
GEMINI_API_KEY_1="key_one..."
GEMINI_API_KEY_2="key_two..."
GEMINI_API_KEY_3="key_three..."
```

*(Note: A single `GEMINI_API_KEY` is also supported, but using the numbered pattern allows for rotation.)*

### 2. Model Priority (Optional)
You can customize the order in which models are attempted by setting `GEMINI_MODELS` in `.env`. The library processes models in **Primary -> Secondary** pairs.

**Default Behavior (if not set):**
1.  `gemini-flash-latest` -> `gemini-flash-lite-latest`
2.  `gemini-3-flash-preview` -> `gemini-2.5-flash`
3.  `gemini-2.5-flash-lite` -> `gemini-2.0-flash`
4.  `gemini-2.0-flash-lite` -> (None)

**Custom Configuration:**
```env
GEMINI_MODELS='["gemini-2.5-flash", "gemini-2.5-flash-lite", "gemini-2.0-flash"]'
```

## 🔍 How it Works

```mermaid
graph TD
    Start[Start Request] --> LoopPairs{Loop Model Pairs}
    LoopPairs -->|Primary, Secondary| LoopClients{Loop API Clients}
    
    LoopClients -->|Next Client| AttemptPrimary[Attempt Primary Model]
    
    AttemptPrimary -->|Success| ReturnResponse[Return Response]
    AttemptPrimary -->|Failure| CheckSecondary{Has Secondary Model?}
    
    CheckSecondary -->|Yes| AttemptSecondary[Attempt Secondary Model]
    CheckSecondary -->|No| NextClient[Next Client]
    
    AttemptSecondary -->|Success| ReturnResponse
    AttemptSecondary -->|Failure| NextClient
    
    NextClient -->|Clients Exhausted| NextPair[Next Pair]
    NextPair -->|Pairs Exhausted| RaiseError[Raise AllClientsFailed]
    
    style Start fill:#f9f,stroke:#333,stroke-width:2px
    style ReturnResponse fill:#9f9,stroke:#333,stroke-width:2px
    style RaiseError fill:#f99,stroke:#333,stroke-width:2px
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
