from offline_mcp import server

_fn = lambda name: (getattr(server, name).fn if hasattr(getattr(server, name), "fn") else getattr(server, name))


import json


def test_no_tool_tells_the_user_to_pipe_a_download_into_a_shell_or_names_the_old_domain():
    outs = [_fn("check_ollama_status")(), _fn("degraded_mode_guide")()] + [_fn("local_deployment_guide")(d) for d in ("laptop", "raspberry_pi", "zzz")]
    text = json.dumps(outs)
    assert "| sh" not in text and "ollama.ai" not in text and "ollama.com/download" in text
