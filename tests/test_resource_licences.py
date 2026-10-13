from offline_mcp import server

_fn = lambda name: (getattr(server, name).fn if hasattr(getattr(server, name), "fn") else getattr(server, name))


def test_the_speech_and_translation_resources_state_their_licence_limits():
    res = {r["name"].split(" ")[0]: r for r in _fn("open_weights_directory")(None)["speech_and_translation_resources"]}
    assert "NC" in res["AfriNLLB"]["licence"] and "non-commercial" in res["AfriNLLB"]["licence"]
    assert "SA" in res["WAXAL"]["licence"] and "not confirmed" in res["WAXAL"]["african_languages"]
    assert res["Paza"]["licence"] == "MIT" and "not an OSI" in res["TranslateGemma"]["licence"]


def test_the_deployment_note_no_longer_claims_everything_runs_on_ollama():
    assert "All models above can be deployed locally via Ollama" not in str(_fn("open_weights_directory")(None))
