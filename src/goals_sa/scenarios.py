from pathlib import Path


def generate_scenarios(dest_path: Path | str) -> None:
    """Generate a scenarios file.

    Docs to do, what format of input will this take?

    Args:
        dest_path: Path where the generated scenarios file will be saved.

    Raises:
        FileNotFoundError: If the destination directory does not exist.
    """
    dest_path = Path(dest_path).resolve()
    if not dest_path.parent.exists():
        err_msg = f"Destination directory does not exist: {dest_path.parent}"
        raise FileNotFoundError(err_msg)
    raise NotImplementedError("Generate scenarios not implemented yet.")
