def get_response(action="monitor"):
    responses = {
        "monitor": "System is actively monitored.",
        "block": "Threat detected and blocked.",
        "isolate": "Endpoint isolation initiated.",
        "recover": "Recovery process initiated."
    }

    return responses.get(action, "System monitoring active.")
