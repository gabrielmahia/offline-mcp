"""OfflineMCP — Local AI Inference Infrastructure (6 tools).
Layer 4: Never assume OpenAI survives or stays accessible.
Build for local inference, open weights, degraded operation.
"""
from __future__ import annotations
from typing import Optional
from fastmcp import FastMCP
mcp = FastMCP(name="offline-mcp", instructions="Local AI inference infrastructure for Africa — Ollama, open weights, degraded-mode fallbacks. 6 tools.")

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

@mcp.tool(name="check_ollama_status", description="Check if Ollama is running locally and list available models.")
def check_ollama_status() -> dict:
    import urllib.request as ur
    try:
        req = ur.Request("http://localhost:11434/api/tags", headers={"User-Agent": "offline-mcp/1.0"})
        with ur.urlopen(req, timeout=3) as r:
            d = __import__("json").loads(r.read())
            models = [m["name"] for m in d.get("models", [])]
            return {"ollama_running": True, "models_available": models,
                    "count": len(models), "api_endpoint": "http://localhost:11434"}
    except Exception as e:
        return {"ollama_running": False, "error": str(e),
                "install_guide": "curl https://ollama.ai/install.sh | sh",
                "windows": "Download from ollama.ai/download",
                "note": "Ollama provides local AI inference — no internet required once models are downloaded."}

@mcp.tool(name="run_local_inference", description="Run a prompt through a local Ollama model.")
def run_local_inference(prompt: str, model: Optional[str] = "llama3.2:3b") -> dict:
    import urllib.request as ur
    import json as js
    data = js.dumps({"model": model, "prompt": prompt, "stream": False}).encode()
    try:
        req = ur.Request("http://localhost:11434/api/generate",
                         data=data, method="POST",
                         headers={"Content-Type":"application/json","User-Agent":"offline-mcp/1.0"})
        with ur.urlopen(req, timeout=60) as r:
            result = js.loads(r.read())
            return {"status": "ok", "model": model, "response": result.get("response",""),
                    "offline": True, "tokens": result.get("eval_count", 0)}
    except Exception as e:
        return {"status": "error", "error": str(e),
                "fallback": "Ollama not running. Start with: ollama serve",
                "offline": False}

@mcp.tool(name="list_recommended_models", description="List recommended open-weight models for East Africa AI use cases.")
def list_recommended_models(use_case: Optional[str] = None, max_ram_gb: Optional[int] = None) -> dict:
    models = RECOMMENDED_MODELS
    if max_ram_gb:
        models = [m for m in models if m["ram_gb"] <= max_ram_gb]
    if use_case:
        u = use_case.lower()
        models = [m for m in models if u in m["use_case"].lower() or u in m["africa_fit"].lower()] or models
    return {"source": "Ollama model registry", "recommended_for_africa": models,
            "install_commands": [m["command"] for m in models],
            "note": "All models run locally — no API key, no internet after download, no cost per query."}

@mcp.tool(name="degraded_mode_guide", description="Guide for operating AI systems when cloud connectivity fails.")
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
                "step_1": "Install Ollama: curl https://ollama.ai/install.sh | sh",
                "step_2": "Download a model: ollama pull llama3.2:3b (2GB)",
                "step_3": "Test: ollama run llama3.2:3b 'Hello, what is the KRA PIN number format?'",
                "step_4": "Configure MCP clients to use localhost:11434 as fallback",
            },
            "hardware_minimums": {"ram_gb": 4, "storage_gb": 5, "cpu": "Any modern CPU (no GPU required for 3B models)"},
            "raspberry_pi": "Ollama runs on Raspberry Pi 4 (4GB RAM) — viable for rural offline deployments."}

@mcp.tool(name="open_weights_directory", description="Directory of open-weight AI models suitable for East Africa civic use cases.")
def open_weights_directory(use_case: Optional[str] = None) -> dict:
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
            "deployment": "All models above can be deployed locally via Ollama or llama.cpp."}

@mcp.tool(name="local_deployment_guide", description="Guide to deploying local AI inference on modest hardware in Kenya/East Africa.")
def local_deployment_guide(device_type: Optional[str] = "laptop") -> dict:
    GUIDES = {
        "laptop": {
            "recommended_model": "llama3.2:3b or gemma2:2b",
            "min_specs": "4GB RAM, 5GB storage, any modern CPU",
            "setup": "1. Install Ollama (ollama.ai) 2. ollama pull llama3.2:3b 3. ollama serve",
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
            "setup": "curl https://ollama.ai/install.sh | sh && ollama pull gemma2:2b",
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
