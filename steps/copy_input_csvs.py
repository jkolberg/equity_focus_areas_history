from __future__ import annotations

import shutil
from pathlib import Path


def run_step(context: dict) -> None:
	paths = context["paths"]
	input_files: dict[str, Path] = context.get("input_files", {})
	inputs_dir: Path | None = paths.get("inputs")
	data_dir: Path = paths["data"]

	if not input_files:
		return

	missing_targets = [path for path in input_files.values() if not path.exists()]
	if not missing_targets:
		return

	if inputs_dir is None:
		raise ValueError("inputs_dir must be set in configs/settings.yaml when input files are missing.")
	if not inputs_dir.exists():
		raise FileNotFoundError(f"Configured inputs_dir does not exist: {inputs_dir}")

	data_dir.mkdir(parents=True, exist_ok=True)

	for target_path in missing_targets:
		source_path = inputs_dir / target_path.name
		if not source_path.exists():
			raise FileNotFoundError(
				f"Missing input file in both data_dir and inputs_dir: {target_path.name}"
			)

		target_path.parent.mkdir(parents=True, exist_ok=True)
		shutil.copy2(source_path, target_path)
