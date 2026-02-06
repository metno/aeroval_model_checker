import typer
from typing import Annotated
from pathlib import Path
from rich import print
import pyaerocom as pya

from utils import (
    print_error,
    print_success,
    filename_checker,
    print_debug,
    init_pya,
    try_read,
    check_modeldata,
)

app = typer.Typer()


@app.command()
def main(
    model_dir: Annotated[
        Path,
        typer.Argument(
            help="Path to folder where you have the model. Only one model id per folder, but can have many years and pollutants",
        ),
    ],
    verbose: Annotated[
        bool,
        typer.Option(
            "--verbose",
            "-v",
            help="If verbose, more info about what the model files contain is printed",
        ),
    ] = False,
    strict: Annotated[
        bool,
        typer.Option(
            "--strict",
            "-s",
            help="If strict everything will be check, even things that might be okay...",
        ),
    ] = False,
):

    # Checking model directory
    print(":recycling_symbol: Looking for Models:")
    if not model_dir.is_dir():
        print_error("The given model dir is not a dir")
        return

    model_files = list(model_dir.glob("*.nc"))

    if len(list(model_files)) == 0:
        print_error("Could not find any files in model dir")
        return

    print_success(f"Found {len(list(model_files))} files")

    # Checking of filenames
    found_model = ""
    print(":recycling_symbol: Checking Filenames:")
    for model in model_files:
        if verbose:
            print_debug(f"Checking file {model.stem}")
        metadata, error = filename_checker(model.stem, strict)
        if error != "":
            print_error(error)
            return

        if found_model == "":
            found_model = metadata["model"]

        if found_model != metadata["model"]:
            print_error(
                f"Found more than one model in folder: {found_model} and {metadata['model']}. Place in two different folders."
            )
            return
    print_success("All Filenames Look Good!")

    # Read modelfiles with xarray
    print(":recycling_symbol: Checking Model Files with Xarray")
    for model in model_files:
        if verbose:
            print_debug(f"Checking file {model.stem}")

        error = check_modeldata(model, strict)

        if error != "":
            print_error(error)
            return

    # Initialize Pyaerocom
    print(":recycling_symbol: Trying to Initiate Pyaerocom Reader with model")

    reader, error = init_pya(model_dir)

    if error != "":
        print_error(f"Failed to initial pyaerocom reader due to error: {error}")

    if verbose:
        print_debug(f"{reader}")
    print_success("Managed to initial Pyaerocom Reader")

    # Reading
    print(":recycling_symbol: Trying to Read Model Data")
    for v in reader.vars_provided:
        if verbose:
            print_debug(f"Trying to load {v}")

        data, error = try_read(reader, v)

        if error != "":
            print_error(error)
            return

    print_success(
        "Everything worked! File is still not guaranteed to work, but the chances have increased :fireworks:"
    )


if __name__ == "__main__":
    app()
