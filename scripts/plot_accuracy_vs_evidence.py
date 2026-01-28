"""Script to plot F1 score vs. evidence F1 for property extraction tasks.

Usage:
    python scripts/plot_accuracy_vs_evidence.py

"""

import pbench

import pandas as pd
from argparse import ArgumentParser
import matplotlib.pyplot as plt
from pathlib import Path

from pbench_eval.plotting_utils import (
    TICK_FONT_SIZE,
    LABEL_FONT_SIZE,
    LEGEND_FONT_SIZE,
)

# Agent -> color mapping for consistent visualization
# zeroshot and terminus-2 use same color but different markers for gpt vs gemini
AGENT_COLORS: dict[str, str] = {
    "zeroshot-gpt": "#555555",  # gray
    "zeroshot-gemini": "#555555",  # gray
    "codex": "#2ca02c",  # green
    "gemini-cli": "#ff7f0e",  # orange
    "terminus-2-gpt": "#d62728",  # red
    "terminus-2-gemini": "#d62728",  # red
}

# Agent -> marker mapping (gpt = circle, gemini = square)
AGENT_MARKERS: dict[str, str] = {
    "zeroshot-gpt": "o",  # circle
    "zeroshot-gemini": "s",  # square
    "codex": "o",  # circle
    "gemini-cli": "o",  # circle
    "terminus-2-gpt": "o",  # circle
    "terminus-2-gemini": "s",  # square
}

# Domain -> display name mapping for plot titles
DOMAIN_ALIASES: dict[str, str] = {
    "supercon": "SuperCon",
    "biosurfactants": "Biosurfactants",
    "cdw": "CDW",
}

# Agent color_key -> legend display name mapping
DISPLAY_NAMES: dict[str, str] = {
    "zeroshot-gpt": "GPT",
    "zeroshot-gemini": "Gemini",
    "codex": "codex",
    "gemini-cli": "gemini-cli",
    "terminus-2-gpt": "terminus-2 (GPT)",
    "terminus-2-gemini": "terminus-2 (Gemini)",
}

# Model -> alpha mapping (large models = high alpha, small models = low alpha)
MODEL_ALPHAS: dict[str, float] = {
    "gpt-5-mini-2025-08-07": 0.4,  # small
    "gemini-3-flash-preview": 0.4,  # small
    "gpt-5.1-2025-11-13": 1.0,  # large
    "gpt-5.2-2025-12-11": 1.0,  # large
    "gemini-3-pro-preview": 1.0,  # large
}

parser = ArgumentParser(
    description="Plot F1 score vs. evidence F1 for property extraction tasks."
)
parser = pbench.add_base_args(parser)
args = parser.parse_args()

pbench.setup_logging(args.log_level)

# Read data from examples subdirectories
output_dirs = [
    ("supercon", Path("examples/supercon-extraction/out-post-2021")),  # harbor
    ("supercon", Path("examples/supercon-extraction/out-post-2021-no-agent")),
    (
        "biosurfactants",
        Path("examples/biosurfactants-extraction/out-biosurfactants"),
    ),  # harbor
    ("biosurfactants", Path("examples/biosurfactants-extraction/out-no-agent")),
]

# Collect data from all output directories
all_data: dict[str, list[dict]] = {"supercon": [], "biosurfactants": []}
for domain, output_dir in output_dirs:
    # Read F1 scores from f1_vs_tokens_summary.csv
    f1_path = output_dir / "tables" / "f1_vs_tokens_summary.csv"
    if not f1_path.exists():
        print(f"Warning: {f1_path} not found, skipping")
        continue
    f1_df = pd.read_csv(f1_path)

    # Read evidence data from evidence_summary.csv
    evidence_path = output_dir / "tables" / "evidence_summary.csv"
    if not evidence_path.exists():
        print(f"Warning: {evidence_path} not found, skipping")
        continue
    evidence_df = pd.read_csv(evidence_path)

    # Select only needed columns before merging to avoid duplicates
    f1_cols = ["agent", "model", "avg_f1_score", "avg_f1_score_sem"]
    evidence_cols = ["agent", "model", "avg_evidence_f1", "avg_evidence_f1_sem"]
    f1_subset = f1_df[[c for c in f1_cols if c in f1_df.columns]]
    evidence_subset = evidence_df[
        [c for c in evidence_cols if c in evidence_df.columns]
    ]

    # Merge on agent and model
    merged = pd.merge(f1_subset, evidence_subset, on=["agent", "model"], how="inner")

    for _, row in merged.iterrows():
        all_data[domain].append(
            {
                "agent": row["agent"],
                "model": row["model"],
                "avg_f1_score": row["avg_f1_score"],
                "avg_f1_score_sem": row.get("avg_f1_score_sem", 0),
                "avg_evidence_f1": row["avg_evidence_f1"],
                "avg_evidence_f1_sem": row.get("avg_evidence_f1_sem", 0),
            }
        )

# Plot with error bars and labels
legend_handles = []
domains = ["supercon", "biosurfactants"]
fig, axs = plt.subplots(1, len(domains), figsize=(3.375, 2.25), sharey=True)
for i, domain in enumerate(domains):
    ax = axs[i]
    data = all_data[domain]
    if not data:
        ax.set_title(DOMAIN_ALIASES.get(domain, domain), fontsize=LABEL_FONT_SIZE)
        ax.text(0.5, 0.5, "No data", ha="center", va="center", transform=ax.transAxes)
        continue

    df = pd.DataFrame(data)

    # Plot each point with color based on agent, alpha based on model
    for idx, row in df.iterrows():
        agent_name = row["agent"]
        model_name = row["model"].split("/")[-1]
        # zeroshot and terminus-2 use different colors based on model provider
        if agent_name in ("zeroshot", "terminus-2"):
            suffix = "-gemini" if "gemini" in model_name else "-gpt"
            color_key = agent_name + suffix
        else:
            color_key = agent_name
        color = AGENT_COLORS.get(color_key, "#333333")
        marker = AGENT_MARKERS.get(color_key, "o")
        alpha = MODEL_ALPHAS.get(model_name, 0.7)
        ax.errorbar(
            row["avg_f1_score"],
            row["avg_evidence_f1"],
            xerr=row["avg_f1_score_sem"],
            yerr=row.get("avg_evidence_f1_sem", 0),
            fmt=marker,
            color=color,
            alpha=alpha,
            capsize=0,
        )
        legend_label = DISPLAY_NAMES.get(color_key, color_key)
        if legend_label not in [h.get_label() for h in legend_handles]:
            legend_handles.append(
                plt.Line2D(
                    [0],
                    [0],
                    marker=marker,
                    color="w",
                    markerfacecolor=color,
                    markersize=8,
                    label=legend_label,
                )
            )
    ax.set_title(DOMAIN_ALIASES.get(domain, domain), fontsize=LABEL_FONT_SIZE)
    ax.set_xlabel("F1 Score", fontsize=LABEL_FONT_SIZE)
    if domain == domains[0]:
        ax.set_ylabel("Evidence Recovery Rate", fontsize=LABEL_FONT_SIZE)
    ax.tick_params(axis="both", labelsize=TICK_FONT_SIZE)
    ax.grid(axis="both", alpha=0.3)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

# Add legend for agents at the bottom (only include agents with results)
# Sort handles: GPT/codex variants first (top row), Gemini variants second (bottom row)
gpt_labels = ["GPT", "codex", "terminus-2 (GPT)"]
sorted_handles = sorted(
    legend_handles,
    key=lambda h: (
        0 if h.get_label() in gpt_labels else 1,
        gpt_labels.index(h.get_label()) if h.get_label() in gpt_labels else 0,
    ),
)
fig.legend(
    handles=sorted_handles,
    loc="lower center",
    ncol=3,
    fontsize=LEGEND_FONT_SIZE,
    frameon=False,
    bbox_to_anchor=(0.5, -0.15),
)

plt.tight_layout()
figures_dir = Path("figures")
figures_dir.mkdir(parents=True, exist_ok=True)
fig_name = "f1_vs_evidence.pdf"
fig_path = figures_dir / fig_name
plt.savefig(fig_path, bbox_inches="tight")
print(f"Saved figure to {fig_path}")
plt.close()
