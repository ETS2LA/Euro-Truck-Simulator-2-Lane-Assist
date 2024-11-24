"""Script to analyze JSON files for road and node data structure."""
import json
import os

def analyze_json_file(filepath: str, sample_size: int = 5) -> None:
    """Analyze a JSON file and print its structure."""
    print(f"\nAnalyzing {os.path.basename(filepath)}:")
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if isinstance(data, list) and len(data) > 0:
        print(f"Total entries: {len(data)}")
        print("\nSample entry structure:")
        sample = data[0]
        for key, value in sample.items():
            print(f"  {key}: {type(value).__name__}")

        print("\nFirst {sample_size} entries:")
        for i, entry in enumerate(data[:sample_size]):
            print(f"\nEntry {i + 1}:")
            for key, value in entry.items():
                if key in ['hidden', 'dlcGuard']:
                    print(f"  {key}: {value}")

def main():
    base_path = "/home/ubuntu/attachments/WORKING/WORKING/plugins/Map/data"
    files = [
        "europe-roads.json",
        "europe-nodes.json",
        "europe-prefabs.json"
    ]

    for filename in files:
        filepath = os.path.join(base_path, filename)
        analyze_json_file(filepath)

if __name__ == "__main__":
    main()
