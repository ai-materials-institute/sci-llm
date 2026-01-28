import matplotlib.pyplot as plt

plt.rcParams["font.family"] = "serif"
plt.rcParams["font.serif"] = ["Times New Roman"]

# Single column figures
TICK_FONT_SIZE = 6
MINOR_TICK_FONT_SIZE = 3
LABEL_FONT_SIZE = 9
LEGEND_FONT_SIZE = 7
MARKER_ALPHA = 1
MARKER_SIZE = 3
LINE_ALPHA = 0.75
OUTWARD = 4


def get_display_label(agent: str, model: str, multiline: bool = True) -> str:
    """Get a consistent display label for an agent+model combination.

    Uses the same naming conventions as plot_accuracy_vs_tokens.py legend:
    - zeroshot with GPT model -> "GPT"
    - zeroshot with Gemini model -> "Gemini"
    - codex -> "codex"
    - gemini-cli -> "gemini-cli"
    - terminus-2 with GPT model -> "terminus-2 (GPT)"
    - terminus-2 with Gemini model -> "terminus-2 (Gemini)"
    - qwen -> "Qwen"

    Args:
        agent: The agent name (e.g., "zeroshot", "codex", "terminus-2").
        model: The model name (e.g., "openai/gpt-4", "gemini/gemini-3-pro-preview").
        multiline: If True, split long labels across two lines.

    Returns:
        A formatted display label string.

    """
    model_short = model.split("/")[-1]
    is_gemini = "gemini" in model_short
    sep = "\n" if multiline else " "

    if agent == "zeroshot":
        return "Gemini" if is_gemini else "GPT"
    elif agent == "terminus-2":
        return f"terminus-2{sep}(Gemini)" if is_gemini else f"terminus-2{sep}(GPT)"
    elif agent == "codex":
        return "codex"
    elif agent == "gemini-cli":
        return "gemini-cli"
    elif agent == "qwen":
        return "Qwen"
    return agent
