from __future__ import annotations

import os
from pathlib import Path

from pypyr.pipelinerunner import run as run_pipeline


def main() -> None:
	repo_root = Path(__file__).resolve().parent
	os.chdir(repo_root)
	run_pipeline("configs/settings")


if __name__ == "__main__":
	main()

