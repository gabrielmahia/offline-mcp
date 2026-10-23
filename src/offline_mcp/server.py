"""OfflineMCP — Local AI Inference Infrastructure (6 tools).
Layer 4: Never assume OpenAI survives or stays accessible.
Build for local inference, open weights, degraded operation.
"""
from __future__ import annotations

from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _pkg_version
from typing import Annotated, Optional

from fastmcp import FastMCP
from pydantic import Field

# Annotations tell clients which tools are safe to auto-approve (read-only, no side effects).
READ_ONLY = {"readOnlyHint": True, "idempotentHint": True, "openWorldHint": False}
STATUS = {"readOnlyHint": True, "idempotentHint": True, "openWorldHint": True}  # talks to the local Ollama service
INFER = {"readOnlyHint": True, "idempotentHint": False, "openWorldHint": True}  # model output varies; calls the local Ollama service

try:
    _VERSION = _pkg_version("offline-mcp")
except PackageNotFoundError:  # a source tree that was never installed
    _VERSION = "0+unknown"


mcp = FastMCP(name="offline-mcp", instructions="Local AI inference infrastructure for Africa — Ollama, open weights, degraded-mode fallbacks. 6 tools.", version=_VERSION)

RECOMMENDED_MODELS = [
    {"name": "llama3.2:3b", "size_gb": 2.0, "ram_gb": 4, "use_case": "General civic queries, fast responses",
     "command": "ollama pull llama3.2:3b", "africa_fit": "Excellent for low-RAM devices"},
    {"name": "mistral:7b", "size_gb": 4.1, "ram_gb": 8, "use_case": "Better quality civic reasoning",
     "command": "ollama pull mistral:7b", "africa_fit": "Good for higher-spec devices"},
    {"name": "phi3:mini", "size_gb": 2.3, "ram_gb": 4, "use_case": "Microsoft's compact model, efficient",
     "command": "ollama pull phi3:mini", "africa_fit": "Good balance of speed and quality"},
    {"name": "gemma2:2b", "size_gb": 1.6, "ram_gb": 3, "use_case": "Google's compact model",
     "command": "ollama pull gemma2:2b", "africa_fit": "Best for very low RAM environments"},
    {"name": "qwen2.5:3b", "size_gb": 1.9, "ram_gb": 4, "use_case": "Multilingual including Swahili",
     "command": "ollama pull qwen2.5:3b", "africa_fit": "Strong multilingual support for Swahili"},
]

@mcp.tool(name="check_ollama_status", description="Check whether a local Ollama server is running at localhost:11434 and which models it has. Use before run_local_inference, or when someone asks whether offline AI is ready. Takes no arguments and contacts only your own machine (3 second timeout). Returns ollama_running, the model names, a count and the endpoint, or ollama_running false with the error and a link to the official download page. Read-only: it only lists models.", annotations=STATUS)
def check_ollama_status() -> dict:
    import urllib.request as ur
    try:
        req = ur.Request("http://localhost:11434/api/tags", headers={"User-Agent": "offline-mcp/1.0"})
        with ur.urlopen(req, timeout=3) as r:
            d = __import__("json").loads(r.read())
            models = [m["name"] for m in d.get("models", [])]
            return {"ollama_running": True, "models_available": models,
                    "count": len(models), "api_endpoint": "http://localhost:11434"}
    except Exception as e:  # noqa: BLE001  (tool boundary: return the error to the model instead of crashing the server)
        return {"ollama_running": False, "error": str(e),
                "install_guide": "Download the installer from https://ollama.com/download",
                "windows": "Download from ollama.com/download",
                "note": "Ollama provides local AI inference — no internet required once models are downloaded."}

@mcp.tool(name="run_local_inference", description="Send a prompt to a local Ollama model and return its answer, with no internet needed once the model is downloaded. Use when no cloud model is reachable or the text must stay on the machine. The prompt goes only to Ollama at localhost:11434 (60 second timeout, non-streaming) and nothing is stored by this tool. Returns the response text, the model used, the token count and offline true, or an error with a hint to start Ollama if it is not running. Read-only with respect to your data; it uses local compute, and answers from small models can be wrong.", annotations=INFER)
def run_local_inference(prompt: Annotated[str, Field(description="The text to send to the local model. It is sent only to localhost.")], model: Annotated[str | None, Field(description="Ollama model name (default llama3.2:3b); it must already be pulled.")] = "llama3.2:3b") -> dict:
    import json as js
    import urllib.request as ur
    data = js.dumps({"model": model, "prompt": prompt, "stream": False}).encode()
    try:
        req = ur.Request("http://localhost:11434/api/generate",
                         data=data, method="POST",
                         headers={"Content-Type":"application/json","User-Agent":"offline-mcp/1.0"})
        with ur.urlopen(req, timeout=60) as r:
            result = js.loads(r.read())
            return {"status": "ok", "model": model, "response": result.get("response",""),
                    "offline": True, "tokens": result.get("eval_count", 0)}
    except Exception as e:  # noqa: BLE001  (tool boundary: return the error to the model instead of crashing the server)
        return {"status": "error", "error": str(e),
                "fallback": "Ollama not running. Start with: ollama serve",
                "offline": False}

@mcp.tool(name="list_recommended_models", description="Recommend open-weights models that run locally through Ollama, with size, RAM need, use case and language fit for Africa. Use when someone asks which model to install for their hardware or task. max_ram_gb keeps models that fit; use_case filters by matching text and, if nothing matches, ALL models are returned. Returns the source label, the recommended models, their install commands and a note that they run locally. A curated list labelled by the author, not a benchmark: check model cards. Read-only; no side effects.", annotations=READ_ONLY)
def list_recommended_models(use_case: Annotated[str | None, Field(description="Optional use case such as translation or coding.")] = None, max_ram_gb: Annotated[int | None, Field(description="Optional RAM limit in GB; keeps models that fit.")] = None) -> dict:
    models = RECOMMENDED_MODELS
    if max_ram_gb:
        models = [m for m in models if m["ram_gb"] <= max_ram_gb]
    if use_case:
        u = use_case.lower()
        models = [m for m in models if u in m["use_case"].lower() or u in m["africa_fit"].lower()] or models
    return {"source": "Ollama model registry", "recommended_for_africa": models,
            "install_commands": [m["command"] for m in models],
            "note": "All models run locally — no API key, no internet after download, no cost per query."}

@mcp.tool(name="degraded_mode_guide", description="Guide to running AI when connectivity or power is unreliable: why it matters, how to install Ollama, pull a small model, test it and point MCP clients at localhost, with hardware minimums and a Raspberry Pi note. Use when planning an offline or low-bandwidth deployment. Takes no arguments. Returns the explanation, numbered setup steps, hardware minimums and deployment tips. A static guide: follow the vendor's own install instructions at ollama.com. Read-only; no side effects.", annotations=READ_ONLY)
def degraded_mode_guide() -> dict:
    return {"source": "AI-KungFU offline architecture guide",
            "why_this_matters": "Kenya's connectivity is improving but remains unreliable outside Nairobi/Mombasa. Power outages, data costs, and latency can make cloud AI unusable.",
            "degraded_mode_levels": {
                "level_1_full_online": "Cloud AI + all MCP servers. Best quality. Requires stable internet.",
                "level_2_local_llm": "Ollama local model + MCP servers. Good quality. Requires local setup.",
                "level_3_cached_responses": "Pre-cached MCP responses + local model. Acceptable quality. Fully offline.",
                "level_4_static_reference": "Static lookup tables and reference data only. No AI inference.",
            },
            "implementation": {
                "step_1": "Install Ollama from https://ollama.com/download",
                "step_2": "Download a model: ollama pull llama3.2:3b (2GB)",
                "step_3": "Test: ollama run llama3.2:3b 'Hello, what is the KRA PIN number format?'",
                "step_4": "Configure MCP clients to use localhost:11434 as fallback",
            },
            "hardware_minimums": {"ram_gb": 4, "storage_gb": 5, "cpu": "Any modern CPU (no GPU required for 3B models)"},
            "raspberry_pi": "Ollama runs on Raspberry Pi 4 (4GB RAM) — viable for rural offline deployments."}

@mcp.tool(name="open_weights_directory", description="Directory of open-weights model families with sizes, languages and licences, including African-language support such as Aya and Masakhane work, plus speech and translation resources (WAXAL, Paza, AfriNLLB, TranslateGemma) with their licences. Use when someone asks which open models or datasets cover Swahili or other African languages, or what the licence allows. use_case filters the language models by matching text; if nothing matches, ALL models are returned. Returns the source label, the language models, an Africa note, how to deploy them locally and the speech and translation resources with licence and coverage caveats. A curated starting list, not exhaustive or benchmarked: check each model card for languages and licence. Read-only; no side effects.", annotations=READ_ONLY)
def open_weights_directory(use_case: Annotated[str | None, Field(description="Optional filter text such as swahili.")] = None) -> dict:
    MODELS = [
        {"name": "Llama 3.2 (Meta)", "sizes": ["1B", "3B", "11B"], "languages": ["en", "sw (limited)"],
         "licence": "Llama 3.2 Community License (free for most uses)", "source": "ollama pull llama3.2"},
        {"name": "Mistral 7B (Mistral AI)", "sizes": ["7B"], "languages": ["en", "fr"],
         "licence": "Apache 2.0 — completely free and open", "source": "ollama pull mistral"},
        {"name": "Gemma 2 (Google)", "sizes": ["2B", "9B", "27B"], "languages": ["en", "multilingual"],
         "licence": "Gemma Terms of Use (free for most uses)", "source": "ollama pull gemma2:2b"},
        {"name": "Qwen 2.5 (Alibaba)", "sizes": ["0.5B", "1.5B", "3B", "7B"], "languages": ["en", "zh", "sw (good)"],
         "licence": "Apache 2.0", "source": "ollama pull qwen2.5:3b"},
        {"name": "Aya Expanse (Cohere for AI)", "sizes": ["8B", "32B"], "languages": ["101 languages including sw"],
         "licence": "CC BY-NC 4.0", "source": "huggingface.co/CohereForAI/aya-expanse-8b"},
        {"name": "AfroLM / AfriBERTa (Masakhane)", "sizes": ["Various"], "languages": ["African languages"],
         "licence": "Apache 2.0", "source": "huggingface.co/masakhane"},
    ]
    if use_case:
        u = use_case.lower()
        MODELS = [m for m in MODELS if u in str(m).lower()] or MODELS
    return {"source": "HuggingFace, Ollama, Masakhane", "open_models": MODELS,
            "africa_note": "Aya Expanse and Masakhane models have best African language support.",
            "deployment": "The language models above can be run locally via Ollama or llama.cpp. The speech and translation resources below use other runtimes: see each model card.",
            "speech_and_translation_resources": [
                {"name": "WAXAL (google/WaxalNLP)", "kind": "speech dataset", "licence": "CC-BY-SA-4.0 and CC-BY-4.0 are both listed: check the licence of each language configuration before use (share-alike has obligations)", "african_languages": "29 language codes listed, including Swahili (swa_tts) and Kikuyu (kik_tts), which are text-to-speech configurations; speech-recognition data for them is not confirmed"},
                {"name": "Paza (microsoft/paza-whisper-large-v3-turbo, microsoft/paza-Phi-4-multimodal-instruct)", "kind": "speech recognition models", "licence": "MIT", "african_languages": "see the model card for which languages are covered"},
                {"name": "AfriNLLB (AfriNLP/AfriNLLB-*)", "kind": "translation models", "licence": "CC-BY-NC-4.0: non-commercial use only", "african_languages": "see the model card for which languages are covered"},
                {"name": "TranslateGemma (google/translategemma-*)", "kind": "translation models", "licence": "Gemma terms of use, not an OSI open-source licence", "african_languages": "see the model card for which languages are covered"},
            ],
            "resources_checked": "2026-10-13 against Hugging Face metadata; language coverage and quality are not benchmarked here"}

@mcp.tool(name="local_deployment_guide", description="Setup guide for running a local model on a device type: laptop, Raspberry Pi and others in the table, with hardware, install steps and a model suggestion. Use when someone asks how to deploy offline AI on specific hardware. An unrecognised device_type returns the laptop guide. Returns the source label, the device_type, the guide, all_options and a solar note. A static guide: follow the vendor's install instructions. Read-only; no side effects.", annotations=READ_ONLY)
def local_deployment_guide(device_type: Annotated[str | None, Field(description="laptop (default), raspberry_pi or another device in the table.")] = "laptop") -> dict:
    GUIDES = {
        "laptop": {
            "recommended_model": "llama3.2:3b or gemma2:2b",
            "min_specs": "4GB RAM, 5GB storage, any modern CPU",
            "setup": "1. Install Ollama (ollama.com/download) 2. ollama pull llama3.2:3b 3. ollama serve",
            "inference_speed": "~5-20 tokens/second on 4-core CPU",
        },
        "server": {
            "recommended_model": "mistral:7b or llama3.1:8b",
            "min_specs": "16GB RAM, 20GB storage, 4+ core CPU",
            "setup": "Docker: docker run -p 11434:11434 ollama/ollama",
            "inference_speed": "~20-50 tokens/second",
        },
        "raspberry_pi": {
            "recommended_model": "gemma2:2b or llama3.2:1b",
            "min_specs": "Raspberry Pi 4 with 4GB RAM, 16GB microSD",
            "setup": "Install Ollama from https://ollama.com/download, then: ollama pull gemma2:2b",
            "inference_speed": "~2-5 tokens/second (usable for simple queries)",
            "power": "~15W — solar-compatible for off-grid deployments",
        },
        "android": {
            "recommended_model": "llama3.2:1b via llama.cpp",
            "app": "PocketPal AI (open source) or MLC Chat",
            "min_specs": "Android phone with 6GB+ RAM",
            "note": "Experimental but viable for very simple queries.",
        },
    }
    guide = GUIDES.get(device_type.lower(), GUIDES["laptop"])
    return {"source": "AI-KungFU offline deployment guide", "device_type": device_type,
            **guide, "all_options": list(GUIDES.keys()),
            "solar_note": "Ollama on Raspberry Pi can run on a 50W solar panel — viable for rural Kenya clinics, schools, and offices."}

def main() -> None:
    """Console entry point."""
    mcp.run()
