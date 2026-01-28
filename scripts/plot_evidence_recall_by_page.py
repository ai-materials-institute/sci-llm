"""Script to plot evidence recall by page number for each agent/model combination.

Usage:
    python scripts/plot_evidence_recall_by_page.py

Generates:
    - figures/evidence_recall_by_page.pdf

"""

import pandas as pd
from argparse import ArgumentParser
import matplotlib.pyplot as plt
from pathlib import Path

import pbench
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

# Agent -> line style mapping (gpt = solid, gemini = dashed)
AGENT_LINESTYLES: dict[str, str] = {
    "zeroshot-gpt": "-",
    "zeroshot-gemini": "--",
    "codex": "-",
    "gemini-cli": "-",
    "terminus-2-gpt": "-",
    "terminus-2-gemini": "--",
}

# Domain -> display name mapping for plot titles
DOMAIN_ALIASES: dict[str, str] = {
    "supercon": "SuperCon",
    "biosurfactants": "Biosurfactants",
    "cdw": "CDW",
}

# Agent color_key -> legend display name mapping for bottom row (agent harness)
DISPLAY_NAMES_AGENT: dict[str, str] = {
    "codex": "codex",
    "gemini-cli": "gemini-cli",
    "terminus-2-gpt": "terminus-2 (GPT)",
    "terminus-2-gemini": "terminus-2 (Gemini)",
}

# Model aliases for shorter display in top row (zeroshot)
MODEL_ALIASES: dict[str, str] = {
    "gemini-3-pro-preview": "gemini 3 pro",
    "gemini-3-flash-preview": "gemini 3 flash",
    "gpt-5-mini-2025-08-07": "gpt 5 mini",
    "gpt-5.1-2025-11-13": "gpt 5.1",
    "gpt-5.2-2025-12-11": "gpt 5.2",
}

# Color mapping for zeroshot models (top row)
# GPT family: blue shades (darker = larger model)
# Gemini family: orange shades (darker = larger model)
MODEL_COLORS: dict[str, str] = {
    "gpt 5.2": "#1f77b4",  # dark blue (larger)
    "gpt 5 mini": "#7fbfff",  # light blue (smaller)
    "gemini 3 pro": "#d95f02",  # dark orange (larger)
    "gemini 3 flash": "#fdae61",  # light orange (smaller)
}

# Line styles for zeroshot models (GPT = solid, Gemini = dashed)
MODEL_LINESTYLES: dict[str, str] = {
    "gpt 5.2": "-",
    "gpt 5 mini": "-",
    "gemini 3 pro": "--",
    "gemini 3 flash": "--",
}

parser = ArgumentParser(
    description="Plot evidence recall by page number for each agent/model."
)
parser = pbench.add_base_args(parser)
parser.add_argument(
    "--max_page",
    type=int,
    default=60,
    help="Maximum page number to display on x-axis (default: 60)",
)
args = parser.parse_args()

pbench.setup_logging(args.log_level)

# Read evidence recall by page from examples subdirectories
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
all_data: dict[str, list[pd.DataFrame]] = {"supercon": [], "biosurfactants": []}
for domain, output_dir in output_dirs:
    recall_path = output_dir / "tables" / "evidence_recall_by_page.csv"
    if not recall_path.exists():
        print(f"Warning: {recall_path} not found, skipping")
        continue
    df = pd.read_csv(recall_path)
    all_data[domain].append(df)

# Check if we have any data
has_data = any(dfs for dfs in all_data.values())
if not has_data:
    print(
        "No data found. Run pbench-score-evidence first to generate "
        "evidence_recall_by_page.csv tables."
    )
    exit(1)

figures_dir = Path("figures")
figures_dir.mkdir(parents=True, exist_ok=True)

# Filter to domains that have data
domains = [d for d in ["supercon", "biosurfactants"] if all_data.get(d)]

# Create 2x2 subplot: top row = zeroshot, bottom row = agent harness
fig, axs = plt.subplots(2, len(domains), figsize=(6.75, 4.5), sharey=True)

# Row labels for the plot
row_labels = ["Zeroshot", "Agent Harness"]

# Define which agents belong to each row
zeroshot_agents = {"zeroshot"}
agent_harness_agents = {"codex", "gemini-cli", "terminus-2"}

# Separate legend tracking for top (zeroshot) and bottom (agent harness) rows
top_legend_handles: list = []
top_legend_labels: list[str] = []
bottom_legend_handles: list = []
bottom_legend_labels: list[str] = []

for row_idx, (row_label, agent_set) in enumerate(
    [(row_labels[0], zeroshot_agents), (row_labels[1], agent_harness_agents)]
):
    for col_idx, domain in enumerate(domains):
        ax = axs[row_idx, col_idx]
        dfs = all_data[domain]

        if not dfs:
            ax.text(
                0.5, 0.5, "No data", ha="center", va="center", transform=ax.transAxes
            )
            continue

        # Combine all DataFrames for this domain
        df_combined = pd.concat(dfs, ignore_index=True)

        # Filter to agents in this row
        df_row = df_combined[df_combined["agent"].isin(agent_set)]

        if df_row.empty:
            ax.text(
                0.5, 0.5, "No data", ha="center", va="center", transform=ax.transAxes
            )
            continue

        # Plot each (agent, model) combination as a line
        for (agent, model), group in df_row.groupby(["agent", "model"]):
            # Sort by page number and filter to max_page
            group = group.sort_values("page")
            group = group[group["page"] <= args.max_page]

            if group.empty:
                continue

            # Determine color_key and display_name based on row
            model_name = model.split("/")[-1]
            model_alias = MODEL_ALIASES.get(model_name, model_name)

            if row_idx == 0:  # Top row (zeroshot) - use model names
                display_name: str = model_alias
                color: str = MODEL_COLORS.get(model_alias, "#333333")
                linestyle: str = MODEL_LINESTYLES.get(model_alias, "-")
            else:  # Bottom row (agent harness) - use agent names
                if agent == "terminus-2":
                    suffix = "-gemini" if "gemini" in model_name else "-gpt"
                    color_key = agent + suffix
                else:
                    color_key = agent
                display_name = DISPLAY_NAMES_AGENT.get(color_key, color_key)
                color = AGENT_COLORS.get(color_key, "#333333")
                linestyle = AGENT_LINESTYLES.get(color_key, "-")

            # Plot line
            line = ax.plot(
                group["page"],
                group["avg_evidence_recall"],
                color=color,
                linestyle=linestyle,
                alpha=0.8,
                linewidth=1.5,
            )[0]

            # Add error band
            ax.fill_between(
                group["page"],
                group["avg_evidence_recall"] - group["avg_evidence_recall_sem"],
                group["avg_evidence_recall"] + group["avg_evidence_recall_sem"],
                color=color,
                alpha=0.15,
            )

            # Add vertical line at max page for this agent/model
            max_page_for_agent = int(group["page"].max())
            ax.axvline(
                x=max_page_for_agent,
                color=color,
                linestyle=linestyle,
                alpha=0.5,
                linewidth=1.0,
            )

            # Track legend entries separately for each row
            if row_idx == 0:  # Top row
                if display_name not in top_legend_labels:
                    top_legend_handles.append(line)
                    top_legend_labels.append(display_name)
            else:  # Bottom row
                if display_name not in bottom_legend_labels:
                    bottom_legend_handles.append(line)
                    bottom_legend_labels.append(display_name)

        # Determine max page for this domain from all data (not just this row)
        domain_max_page = (
            int(df_combined["page"].max()) if not df_combined.empty else args.max_page
        )
        domain_max_page = min(domain_max_page, args.max_page)  # Cap at args.max_page

        # Set labels
        if row_idx == 1:  # Bottom row
            ax.set_xlabel("Page Number", fontsize=LABEL_FONT_SIZE)
        if col_idx == 0:  # Left column
            ax.set_ylabel("Evidence Recall", fontsize=LABEL_FONT_SIZE)
        if row_idx == 0:  # Top row - add domain title
            ax.set_title(DOMAIN_ALIASES.get(domain, domain), fontsize=LABEL_FONT_SIZE)

        # Add row label on the right side
        if col_idx == len(domains) - 1:
            ax.annotate(
                row_label,
                xy=(1.02, 0.5),
                xycoords="axes fraction",
                fontsize=LABEL_FONT_SIZE,
                ha="left",
                va="center",
                rotation=-90,
            )

        ax.tick_params(axis="both", labelsize=TICK_FONT_SIZE)
        ax.grid(axis="both", alpha=0.3)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.set_xlim(1, domain_max_page)
        ax.set_ylim(0, 1)

# Add separate legends for top and bottom rows
# Top row legend (zeroshot): sort by GPT first, then Gemini
if top_legend_handles:
    gpt_model_order = ["gpt 5.2", "gpt 5 mini"]
    gemini_model_order = ["gemini 3 flash", "gemini 3 pro"]
    top_pairs = list(zip(top_legend_handles, top_legend_labels))
    sorted_top = sorted(
        top_pairs,
        key=lambda x: (
            0 if x[1] in gpt_model_order else 1,
            gpt_model_order.index(x[1])
            if x[1] in gpt_model_order
            else gemini_model_order.index(x[1])
            if x[1] in gemini_model_order
            else 99,
        ),
    )
    sorted_top_handles, sorted_top_labels = zip(*sorted_top) if sorted_top else ([], [])

    # Position legend between top and bottom rows
    fig.legend(
        sorted_top_handles,
        sorted_top_labels,
        loc="center",
        ncol=4,
        fontsize=LEGEND_FONT_SIZE,
        frameon=False,
        bbox_to_anchor=(0.5, 0.52),
    )

# Bottom row legend (agent harness): sort by GPT-based first, then Gemini-based
if bottom_legend_handles:
    gpt_agent_order = ["codex", "terminus-2 (GPT)"]
    gemini_agent_order = ["gemini-cli", "terminus-2 (Gemini)"]
    bottom_pairs = list(zip(bottom_legend_handles, bottom_legend_labels))
    sorted_bottom = sorted(
        bottom_pairs,
        key=lambda x: (
            0 if x[1] in gpt_agent_order else 1,
            gpt_agent_order.index(x[1])
            if x[1] in gpt_agent_order
            else gemini_agent_order.index(x[1])
            if x[1] in gemini_agent_order
            else 99,
        ),
    )
    sorted_bottom_handles, sorted_bottom_labels = (
        zip(*sorted_bottom) if sorted_bottom else ([], [])
    )

    fig.legend(
        sorted_bottom_handles,
        sorted_bottom_labels,
        loc="lower center",
        ncol=4,
        fontsize=LEGEND_FONT_SIZE,
        frameon=False,
        bbox_to_anchor=(0.5, -0.02),
    )

plt.tight_layout()
fig_path = figures_dir / "evidence_recall_by_page.pdf"
plt.savefig(fig_path, bbox_inches="tight")
print(f"Saved figure to {fig_path}")
plt.close()
