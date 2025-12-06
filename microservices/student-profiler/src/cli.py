from __future__ import annotations

import argparse
from pathlib import Path

from .api import get_service


def run_train(artifact_path: Path) -> None:
    service = get_service()
    metrics = service.train_and_save(str(artifact_path))
    print("Training complete", metrics)


def main() -> None:
    parser = argparse.ArgumentParser(description="Student profiler CLI")
    parser.add_argument("command", choices=["train"], help="Command to execute")
    args = parser.parse_args()

    config_path = Path(__file__).resolve().parents[1] / "config" / "model_config.yaml"
    artifact_path = Path(__file__).resolve().parents[1] / "artifacts" / "student_profiler.joblib"

    if args.command == "train":
        artifact_path.parent.mkdir(parents=True, exist_ok=True)
        run_train(artifact_path)


if __name__ == "__main__":
    main()

