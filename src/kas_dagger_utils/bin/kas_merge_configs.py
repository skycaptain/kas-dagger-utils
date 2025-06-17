# Kas Utils
#
# SPDX-License-Identifier: BSD-3-Clause
#
import argparse
import json
import logging
import subprocess
import sys
import tempfile
from contextlib import ExitStack
from pathlib import Path
from typing import Any, Dict, List

import yaml

logger = logging.getLogger(__name__)


def detect_file_format(filepath: Path) -> str:
    suffix = filepath.suffix.lower()
    if suffix in [".yaml", ".yml"]:
        return "yaml"
    elif suffix == ".json":
        return "json"
    else:
        raise ValueError(f"Unsupported file format: {suffix}")


def load_yaml_documents(filepath: Path) -> List[Dict[str, Any]]:
    with open(filepath, "r", encoding="utf-8") as f:
        documents = list(yaml.safe_load_all(f))

    # Filter out None documents (empty documents in YAML)
    return [_ for _ in documents if _ is not None]


def load_json_array(filepath: Path) -> List[Dict[str, Any]]:
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, list):
        return data
    else:
        raise ValueError("JSON file must contain an array of objects")


def merge_documents(config: Path, format_: str = "yaml"):
    # Detect input format and load documents
    input_format = detect_file_format(config)

    if input_format == "yaml":
        documents = load_yaml_documents(config)
    elif input_format == "json":
        documents = load_json_array(config)
    else:
        raise ValueError(f"Unsupported input format: {input_format}")

    if not documents:
        raise ValueError("No documents found in input file")

    with ExitStack() as stack:
        config_paths = []

        # Create temporary files for each document
        for document in documents:
            temp_file = stack.enter_context(
                tempfile.NamedTemporaryFile(
                    mode="w",
                    prefix=f"{config.stem}.",
                    suffix=".json",
                    dir=config.parent,
                    delete=True,
                    encoding="utf-8",
                )
            )

            # Write document to temporary file as JSON
            json.dump(document, temp_file)
            temp_file.flush()  # Ensure data is written to disk

            config_paths.append(temp_file.name)

        # Build kas dump command with specified output format
        try:
            subprocess.run(
                ["kas", "dump", "--format", format_, ":".join(config_paths)],
                check=True,
            )
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"kas dump failed with exit code {e.returncode}")

    logger.info("Documents merged successfully")


def main():
    parser = argparse.ArgumentParser(
        description="Merge multi-document YAML/JSON kas configurations into a single document",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    %(prog)s config.yaml > merged.yaml
    %(prog)s config.json --format yaml > merged.yaml
    %(prog)s multi-doc.yaml -f json > output.json
""".strip(),
    )
    parser.add_argument(
        "input_file",
        type=Path,
        help="Input file containing YAML multi-document or JSON array",
    )
    parser.add_argument(
        "-f",
        "--format",
        choices=["json", "yaml"],
        default="yaml",
        help="Output format (default: yaml)",
    )

    args = parser.parse_args()

    # Validate input file exists
    if not args.input_file.exists():
        logger.error("Input file '%s' not found", args.input_file)
        sys.exit(1)

    merge_documents(args.input_file, args.format)


if __name__ == "__main__":
    main()
