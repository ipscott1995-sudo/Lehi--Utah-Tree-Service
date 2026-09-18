from pathlib import Path
import shutil


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "output"


def main():
    if not OUTPUT_DIR.exists():
        raise FileNotFoundError(
            "No output folder found. Generate the site before publishing."
        )

    # Copy generated files/folders into the Git-tracked site root.
    for item in OUTPUT_DIR.iterdir():
        destination = ROOT / item.name

        if item.is_dir():
            if destination.exists():
                shutil.rmtree(destination)
            shutil.copytree(item, destination)
        else:
            shutil.copy2(item, destination)

    print("Site published successfully.")
    print("Generated files copied from output/ to project root.")


if __name__ == "__main__":
    main()