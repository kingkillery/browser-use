# Custom fork features to re‑implement on top of upstream

This fork currently has a small set of custom commits on top of an older `browser-use/browser-use` snapshot. We are resetting `main` to match the latest `upstream/main`, so these notes capture everything that needs to be re‑implemented.

Ahead/behind status before reset:

- **HEAD (main)** was **5 commits ahead** of `upstream/main` and **2428 commits behind**.
- Custom feature commits:
  - `ae5f7964` – Add AnyLLM support and MCP server improvements
  - `a64d0cec` – Add Bytedance UI TARS model support and MCP system prompt
  - `85be0f3f` – Minor README edits (removed 7 lines)

---

## 1. AnyLLM support and MCP server improvements (`ae5f7964`)

### Files touched

- `.env.example`
- `browser_use/agent/service.py`
- `browser_use/agent/views.py`
- `browser_use/cli.py`
- `browser_use/config.py`
- `browser_use/llm/__init__.py`
- `browser_use/llm/any_llm.py`
- `browser_use/llm/base.py`
- `browser_use/llm/exceptions.py`
- `browser_use/llm/messages.py`
- `browser_use/llm/schema.py`
- `browser_use/llm/tests/test_anthropic_cache.py` (removed)
- `browser_use/llm/tests/test_chat_models.py` (removed)
- `browser_use/llm/tests/test_gemini_image.py` (removed)
- `browser_use/llm/tests/test_groq_loop.py` (removed)
- `browser_use/llm/tests/test_single_step.py` (removed)
- `browser_use/llm/views.py`
- `browser_use/logging_config.py`
- `browser_use/mcp/server.py`
- `docs/browser-use-docs-notes.md`
- `docs/pk-code-browser-use-mcp-setup.md`
- `examples/models/openrouter_glm.py`
- `pyproject.toml`
- `test_any_llm_example.py`
- `tests/llm/test_any_llm.py`

### Behavior/feature summary

- Introduces a new **AnyLLM** integration in `browser_use/llm/any_llm.py`.
- Updates LLM base classes and message handling to support AnyLLM.
- Adds documentation for setup and usage (including MCP setup docs and an OpenRouter GLM example).
- Adjusts configuration and CLI to expose AnyLLM‑related options.
- Adds MCP server enhancements tied to the new LLM integration.
- Removes and reorganizes several legacy LLM test files.

### TODOs to re‑implement on top of latest upstream

- **LLM integration**
  - [ ] Recreate `browser_use/llm/any_llm.py` against the latest `browser_use/llm` architecture.
  - [ ] Wire AnyLLM into `browser_use/llm/__init__.py` and any upstream‑updated LLM registration mechanisms.
  - [ ] Reconcile changes in `browser_use/llm/base.py`, `messages.py`, and `schema.py` with upstream’s latest versions and reapply only the minimal necessary AnyLLM‑specific hooks.

- **Config & CLI**
  - [ ] Reintroduce AnyLLM‑related options into `browser_use/config.py` in a way that is compatible with upstream’s current config model.
  - [ ] Re‑add CLI flags/commands in `browser_use/cli.py` for selecting/configuring AnyLLM, aligning with any new CLI patterns.
  - [ ] Update `.env.example` with AnyLLM‑specific environment variables using upstream’s current env conventions.

- **MCP server enhancements**
  - [ ] Reapply the necessary changes to `browser_use/mcp/server.py` on top of upstream, minimizing divergence (e.g., only the hooks needed for AnyLLM).
  - [ ] Ensure MCP behavior matches current upstream expectations (request/response formats, logging, error handling).

- **Logging & agent wiring**
  - [ ] Re‑introduce AnyLLM‑related wiring in `browser_use/agent/service.py` and `browser_use/agent/views.py`, updated to match upstream’s agent architecture.
  - [ ] Re‑apply any necessary changes in `browser_use/logging_config.py` in a way that does not conflict with upstream’s newer logging strategy.

- **Examples & docs**
  - [ ] Recreate the `examples/models/openrouter_glm.py` example (or equivalent) using upstream’s current example structure.
  - [ ] Restore and update AnyLLM documentation from `docs/browser-use-docs-notes.md` and `docs/pk-code-browser-use-mcp-setup.md` so they reflect the latest APIs.

- **Tests**
  - [ ] Recreate `tests/llm/test_any_llm.py` using upstream’s current testing helpers and patterns.
  - [ ] Decide whether to reintroduce or replace removed tests (`test_chat_models`, `test_single_step`, etc.) based on how upstream’s test suite evolved.

---

## 2. Bytedance UI TARS model support and MCP system prompt (`a64d0cec`)

### Files touched

- `browser_use/llm/any_llm.py`
- `browser_use/mcp/system_prompt.md`
- `examples/models/bytedance_ui_tars.py`
- `pyproject.toml`
- `test_direct_any_llm.py`
- `test_openrouter_bytedance.py`
- `tests/ci/test_bytedance_ui_tars_visual.py`

### Behavior/feature summary

- Adds **Bytedance UI TARS** model support, integrated via AnyLLM.
- Extends the MCP **system prompt** to work correctly with the TARS UI model.
- Adds examples and tests for direct AnyLLM usage and Bytedance integration, including a visual CI test.

### TODOs to re‑implement on top of latest upstream

- **Model integration**
  - [ ] Re‑add Bytedance UI TARS configuration into `browser_use/llm/any_llm.py` (or equivalent location in the updated LLM stack).
  - [ ] Ensure model IDs, parameters, and capabilities align with upstream’s latest model abstraction and AnyLLM’s updated design.

- **MCP system prompt**
  - [ ] Reapply the Bytedance‑related changes to `browser_use/mcp/system_prompt.md`, carefully merging with upstream’s latest system prompt design.
  - [ ] Verify that prompt changes comply with any new MCP/system‑prompt guidelines introduced upstream.

- **Examples & tests**
  - [ ] Recreate `examples/models/bytedance_ui_tars.py` using the latest example conventions.
  - [ ] Reintroduce and update `test_direct_any_llm.py` and `test_openrouter_bytedance.py` to match upstream’s current test tooling.
  - [ ] Port `tests/ci/test_bytedance_ui_tars_visual.py` to the new CI layout, or create equivalent coverage if the framework changed.

---

## 3. README edits (`85be0f3f`)

- This commit only removed 7 lines from `README.md`.
- After syncing with upstream, we can:
  - [ ] Re‑evaluate whether we still want those deletions (or equivalent edits) on top of upstream’s current README.

---

## Reimplementation plan (high level)

1. **Sync to upstream**
   - Reset `main` to `upstream/main` and force‑push to `origin/main` (done after this file is committed).

2. **Reintroduce AnyLLM**
   - Implement `any_llm` integration and config/CLI wiring based on the TODOs above.
   - Add/update docs and examples.
   - Restore and adapt tests.

3. **Layer Bytedance UI TARS on top**
   - Add TARS configuration on top of the new AnyLLM integration.
   - Update MCP system prompt and related tests.

4. **Polish & docs**
   - Revisit README changes and ensure they are still relevant.
   - Make sure new features are well documented and tested.
