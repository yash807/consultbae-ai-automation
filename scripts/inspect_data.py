"""Inspect the raw CSV datasets without modifying them."""

from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"


def inspect_csv(file_path: Path) -> None:
    """Print a concise quality report for one CSV file."""

    # Read everything as text so IDs and phone numbers are not altered.
    df = pd.read_csv(file_path, dtype=str)

    print("\n" + "=" * 80)
    print(f"FILE: {file_path.name}")
    print("=" * 80)

    print(f"Rows: {len(df)}")
    print(f"Columns: {len(df.columns)}")

    print("\nCOLUMN NAMES")
    for position, column in enumerate(df.columns, start=1):
        print(f"{position:>2}. {column}")

    print("\nMISSING VALUES")
    missing = df.isna().sum()

    for column in df.columns:
        percentage = (missing[column] / len(df) * 100) if len(df) else 0
        print(
            f"{column:<30} "
            f"{missing[column]:>4} missing "
            f"({percentage:>6.2f}%)"
        )

    exact_duplicates = df.duplicated().sum()
    print(f"\nExact duplicate rows: {exact_duplicates}")

    print("\nUNIQUE VALUE COUNTS")
    for column in df.columns:
        print(f"{column:<30} {df[column].nunique(dropna=True)}")

    print("\nWHITESPACE ISSUES")
    whitespace_found = False

    for column in df.columns:
        values = df[column].dropna()
        padded = values[values != values.str.strip()]

        if not padded.empty:
            whitespace_found = True
            print(f"{column}: {len(padded)} value(s) contain outer whitespace")
            print(f"  Examples: {padded.head(3).tolist()}")

    if not whitespace_found:
        print("No outer-whitespace issues detected.")

    print("\nPOSSIBLE DUPLICATES IN IDENTITY COLUMNS")
    identity_keywords = ("name", "email", "phone", "mobile", "contact")

    identity_columns = [
        column
        for column in df.columns
        if any(keyword in column.lower() for keyword in identity_keywords)
    ]

    if not identity_columns:
        print("No likely identity columns detected.")
    else:
        for column in identity_columns:
            normalized = (
                df[column]
                .dropna()
                .str.strip()
                .str.lower()
            )

            duplicate_values = normalized[
                normalized.duplicated(keep=False)
            ].value_counts()

            print(f"\n{column}:")

            if duplicate_values.empty:
                print("  No repeated normalized values.")
            else:
                print(duplicate_values.head(10).to_string())

    print("\nFIRST FIVE ROWS")
    print(df.head().to_string(index=False))


def main() -> None:
    csv_files = sorted(RAW_DATA_DIR.glob("*.csv"))

    if not csv_files:
        raise FileNotFoundError(
            f"No CSV files were found in {RAW_DATA_DIR}"
        )

    print(f"Found {len(csv_files)} CSV file(s).")

    for file_path in csv_files:
        inspect_csv(file_path)


if __name__ == "__main__":
    main()