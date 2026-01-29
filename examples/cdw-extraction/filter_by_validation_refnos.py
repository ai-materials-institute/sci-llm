"""Filter CDW extraction results by validation reference numbers.

Creates filtered copies of out-0125 for Chao and Fatmagul validation sets.

Usage:
    python filter_by_validation_refnos.py
"""

from pathlib import Path

import pandas as pd

# Define paths
BASE_DIR = Path(__file__).parent
MAIN_CSV = BASE_DIR / "out-0125" / "candidates" / "extracted_properties_combined.csv"
CHAO_CSV = (
    BASE_DIR
    / "out-cdw-papers-chao__for_validation"
    / "candidates"
    / "extracted_properties_combined.csv"
)
FATMAGUL_CSV = (
    BASE_DIR
    / "out-cdw-papers-fatmagul__for_validation"
    / "candidates"
    / "extracted_properties_combined.csv"
)

OUTPUT_CHAO = (
    BASE_DIR / "out-0125-for-chao" / "candidates" / "extracted_properties_combined.csv"
)
OUTPUT_FATMAGUL = (
    BASE_DIR
    / "out-0125-for-fatmagul"
    / "candidates"
    / "extracted_properties_combined.csv"
)


def get_unique_refnos(csv_path: Path) -> set[str]:
    """Extract unique non-empty refno values from a CSV file."""
    df = pd.read_csv(csv_path)
    refnos = df["refno"].dropna().astype(str).unique()
    return set(refnos)


def filter_and_save(
    main_df: pd.DataFrame,
    refnos: set[str],
    output_path: Path,
    label: str,
) -> None:
    """Filter main dataframe by refnos and save to output path."""
    # Convert refno column to string for matching
    main_df["refno"] = main_df["refno"].astype(str)
    filtered_df = main_df[main_df["refno"].isin(refnos)]

    # Create output directory
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Save filtered dataframe
    filtered_df.to_csv(output_path, index=False)

    print(f"{label}:")
    print(f"  Validation refnos: {len(refnos)}")
    print(f"  Matched rows: {len(filtered_df)}")
    print(f"  Unique refnos matched: {filtered_df['refno'].nunique()}")
    print(f"  Saved to: {output_path}")
    print()


# Load main dataset
print(f"Loading main dataset from {MAIN_CSV}")
main_df = pd.read_csv(MAIN_CSV)
print(
    f"Main dataset: {len(main_df)} rows, {main_df['refno'].nunique()} unique refnos\n"
)

# Get refnos from validation sets
chao_refnos = get_unique_refnos(CHAO_CSV)
fatmagul_refnos = get_unique_refnos(FATMAGUL_CSV)

# Filter and save for each validation set
filter_and_save(main_df.copy(), chao_refnos, OUTPUT_CHAO, "Chao")
filter_and_save(main_df.copy(), fatmagul_refnos, OUTPUT_FATMAGUL, "Fatmagul")

print("Done!")
