# offline-mcp

[![offline-mcp Glama score](https://glama.ai/mcp/servers/gabrielmahia/offline-mcp/badges/score.svg)](https://glama.ai/mcp/servers/gabrielmahia/offline-mcp)
[![smithery badge](https://smithery.ai/badge/@gabrielmahia/offline-mcp)](https://smithery.ai/server/@gabrielmahia/offline-mcp)


> Local AI inference infrastructure — Ollama wrapper, open weights directory, degraded-mode guide for East Africa.

[![PyPI](https://img.shields.io/badge/PyPI-v0.1.0-blue?logo=pypi)](https://pypi.org/project/offline-mcp/)
[![Thesis Layer](https://img.shields.io/badge/Thesis_Layer-L4_Offline_AI-red)](https://gabrielmahia.github.io/nairobi-stack)

**Why:** Never assume OpenAI survives, Anthropic stays accessible, or export controls disappear.
This matters more in Africa than anywhere else.

**1st world equivalent:** Ollama, LLaMA, Mistral local deployment


## Why This Exists: Data Sovereignty

> *"If you take the deal, you're going to be exploited. If you don't take it, you're going to die."*  
> — Frank Ssekamwa, Ugandan digital rights expert

Across the Global South, AI and health data from communities is being extracted, processed abroad,
and used to build models whose value flows away from the communities that generated it.

`offline-mcp` is the **sovereignty floor** of the East Africa coordination stack.

When this runs on a Raspberry Pi 4 with a 50W solar panel and a 256GB SD card:
- Health data stays in the clinic. Health guidance comes from local models.
- Land records stay in the land office. Queries don't touch foreign servers.
- Civic data stays in the county. AI assistance runs without internet.

**No API key. No cloud dependency. No data leaving the community.**

The models available via `offline-mcp` (Llama 3.2, Qwen 2.5) run entirely on device.
Community data used to generate AI outputs creates no dataset sent back to model providers.

This is not a privacy feature. It is the architectural foundation of digital independence.

---
## Install
```bash
pip install offline-mcp
```

## Tools (6)
| Tool | Description |
|------|-------------|
| `check_ollama_status` | Check if Ollama is running locally and list available models |
| `run_local_inference` | Run a prompt through a local Ollama model |
| `list_recommended_models` | Best open-weight models for East Africa use cases |
| `degraded_mode_guide` | 4-level degraded mode architecture for offline operation |
| `open_weights_directory` | Directory of open-weight models with Africa language support |
| `local_deployment_guide` | Deployment guide for laptop, server, Raspberry Pi, Android |

## Context
Runs on a 50W solar panel + Raspberry Pi 4. Viable for rural Kenya clinics, schools, and community offices.

→ [The Nairobi Stack](https://gabrielmahia.github.io/nairobi-stack)

## License
MIT © Gabriel Mahia | contact@aikungfu.dev
