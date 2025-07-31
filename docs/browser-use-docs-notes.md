# Browser-Use Documentation Notes

## 1. CLI Usage

-   **Interactive Mode:** `uvx browser-use`
-   **One-Shot Mode:** `uvx browser-use -p "Your task"`
-   **MCP Server Mode:** `uvx browser-use --mcp`
-   **Configuration:**
    -   Default config file: `~/.config/browseruse/config.json`
    -   Override with `BROWSER_USE_CONFIG_PATH` or `BROWSER_USE_CONFIG_DIR` env vars.
    -   Environment variables always override the config file.

## 2. Browser Settings & Connection

-   **`BrowserSession`:** Manages the live connection to a browser.
-   **`BrowserProfile`:** A reusable template for `BrowserSession` configurations.
-   **Connection Methods:**
    -   Launch a new browser instance (default).
    -   Connect to a running browser via:
        -   WSS URL (`wss_url`)
        -   CDP URL (`cdp_url`)
        -   Process ID (`browser_pid`)
-   **Key Configuration Options:**
    -   `headless`: Run in headless mode.
    -   `user_data_dir`: Persistent browser profile. Set to `None` for incognito.
    -   `storage_state`: Share cookies, localStorage, etc., between sessions.
    -   `allowed_domains`: Restrict which domains the agent can visit.
    -   `stealth`: Use `patchright` to evade bot detection.

## 3. Agent Configuration

-   **`Agent(...)`:** The core class for running automation tasks.
-   **Key Parameters:**
    -   `task`: The natural language instruction for the agent.
    -   `llm`: The language model to use (e.g., `ChatOpenAI`, `ChatAnthropic`).
    -   `controller`: A registry for custom actions.
    -   `sensitive_data`: A dictionary to handle secrets securely.
    -   `use_vision`: Enable or disable vision capabilities for the model.
-   **Planner Model:** A separate, smaller model can be used for high-level planning (`planner_llm`).

## 4. Interacting with the GUI

-   **Visual Tasks:** For tasks requiring visual understanding of the GUI, the `bytedance/ui-tars-1.5-7b` model on OpenRouter is recommended. This can be configured via an OpenAI-compatible API.
-   **Element Highlighting:** `highlight_elements=True` in `BrowserProfile` or `BrowserSession` visually marks interactive elements on the page.

## 5. Customization

-   **Custom Functions:**
    -   Define custom actions using the `@controller.action(...)` decorator.
    -   Functions can be `sync` or `async`.
    -   Parameters can be defined directly as function arguments or using a Pydantic `BaseModel`.
    -   Access browser APIs via framework-provided parameters like `page: Page` and `browser_session: BrowserSession`.
-   **Lifecycle Hooks:**
    -   `on_step_start` and `on_step_end` hooks allow executing custom code at different stages of the agent's run.
-   **Output Formatting:**
    -   Define a Pydantic `BaseModel` and pass it to `Controller(output_model=...)` to enforce a structured JSON output.

## 6. Handling Sensitive Data

-   Use the `Agent(sensitive_data=...)` parameter.
-   The keys are placeholder names (e.g., `x_password`) used in the prompt, and the values are the actual secrets.
-   The agent replaces the placeholders with the real values at runtime, so the LLM never sees the secrets.
-   Combine with `BrowserSession(allowed_domains=[...])` for enhanced security.
-   Set `use_vision=False` to prevent the model from seeing sensitive data in screenshots.

## 7. MCP Integration

-   **MCP Server:**
    -   Run `browser-use` as an MCP server using `uvx browser-use --mcp`.
    -   Exposes browser automation as tools for clients like Claude Desktop.
    -   Configure in `claude_desktop_config.json`.
-   **MCP Client:**
    -   Allows the `browser-use` agent to connect to external MCP servers (e.g., for filesystem or GitHub access).
    -   Use `MCPClient` to connect and register the external tools with the agent's `Controller`.

## 8. Supported Models

-   Native support for OpenAI, Anthropic, AWS Bedrock, Azure OpenAI, Gemini, and Groq.
-   Supports any model with an OpenAI-compatible API, which is how OpenRouter models like `bytedance/ui-tars-1.5-7b` can be used.
-   Example for OpenAI-compatible API:
    ```python
    from browser_use.llm import ChatOpenAI

    llm = ChatOpenAI(
        model="bytedance/ui-tars-1.5-7b",
        api_key="YOUR_OPENROUTER_KEY",
        base_url="https://openrouter.ai/api/v1"
    )
    ```
