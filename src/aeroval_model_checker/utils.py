from pathlib import Path
from rich import print
import pyaerocom as pya
from iris.cube import Cube
import xarray as xr
from pyaerocom.units import Unit
from pyaerocom.units.helpers import get_standard_unit

# import warnings

# warnings.filterwarnings("error")

VALID_LAYER = ["Surface", "Column"]
VALID_FREQ = ["daily", "hourly", "monthly"]
NUMBER_TIMESTEPS = {"hourly": 8760, "daily": 365, "monthly": 12}


def print_error(msg: str):
    print(f"[bold red]{msg}[/bold red] :red_circle:")


def print_success(msg: str):
    print(f"[bold green]{msg}[/bold green] :green_circle:")


def print_debug(msg: str):
    print(f"[yellow] {msg} [/yellow]")


def filename_checker(filename: str, strict: bool) -> tuple[dict | None, str]:
    results = {}
    error = ""

    parts = filename.split("_")
    if len(parts) != 6 or parts[0] != "aerocom3":
        error = "File name is wrong. Should be on the form aerocom3_MODELNAME_SPECIES_LAYER_YEAR_FREQ.nc"
        return None, error

    model = parts[1]
    poll = parts[2]
    layer = parts[3]
    year = parts[4]
    freq = parts[5]

    if strict:
        if poll not in pya.config.VARS:
            error = f"Pollutant {poll} not allowed. This error might also appear if you have an invalid name for the model"

    if layer not in VALID_LAYER:
        error = f"Layer {layer} not allowed. Please use one of {VALID_LAYER}. This error might also appear if you have an invalid name for the model"
        return None, error

    if freq not in VALID_FREQ:
        error = f"Frequency {freq} not allowed. Please use one of {VALID_FREQ}. This error might also appear if you have an invalid name for the model"
        return None, error

    try:
        i = int(year)
    except:
        error = f"Year {year} is not an int. This error might also appear if you have an invalid name for the model"
        return None, error

    results = dict(model=model, poll=poll, layer=layer, year=year, freq=freq)

    return results, error


def init_pya(model_dir: Path) -> tuple[pya.io.ReadUngridded | None, str]:
    try:
        reader = pya.io.ReadGridded(data_dir=str(model_dir))
        return reader, ""
    except Exception as e:
        return None, str(e)


def try_read(reader: pya.io.ReadGridded, var: str) -> tuple[Cube | None, str]:
    try:
        data = reader.read(var)
        return data, ""
    except Exception as e:
        return None, str(e)


def check_modeldata(modelfile: Path, strict: bool) -> str:
    try:
        data = xr.open_dataset(modelfile, decode_timedelta=True, use_cftime=True)

    except Exception as e:
        return f"Could not open model file {modelfile} due to {str(e)}"

    parts = str(modelfile.stem).split("_")

    model = parts[1]
    poll = parts[2]
    layer = parts[3]
    year = parts[4]
    freq = parts[5]

    if poll not in data:
        return f"Could not find pollutant in file {modelfile}. Make sure name in model file is the same as in file name"

    if "time" not in data:
        return "Time dimension missing"

    # if abs(len(data.time) - NUMBER_TIMESTEPS[freq]) > 2:
    #     return f"Incorrect number of timesteps in file. Expected {NUMBER_TIMESTEPS[freq]}, got {len(data.time)}. Check that frequency in file name matches the actual frequency"

    found_lat = False
    found_lon = False
    for coord in data.coords:
        if "lat" == coord or "latitude" == coord:
            if (
                "standard_name" in data.coords[coord]
                and data.coords[coord].standard_name == "latitude"
            ) or data.coords[coord].long_name == "latitude":
                found_lat = True
        if "lon" == coord or "longitude" == coord:
            if (
                "standard_name" in data.coords[coord]
                and data.coords[coord].standard_name == "longitude"
                or data.coords[coord].long_name == "longitude"
            ):
                found_lon = True

    if not (found_lat and found_lon):
        return "Either latitude or longitude are missing"

    if not (
        poll not in pya.config.VARS and not strict
    ):  # Not 100% sure about this logic...
        try:
            to_unit_str = get_standard_unit(poll)
            to_unit = Unit(to_unit_str, aerocom_var=poll, ts_type=freq)
            current_unit = Unit(data[poll].units, aerocom_var=poll, ts_type=freq)
            if to_unit != current_unit:
                breakpoint()
                return f"Unit of provided pollutant {data[poll].units} can not be converted to {to_unit_str} for {poll}"
        except Exception as e:
            return f"Something went wrong when trying to check the unit of the model file {modelfile}: {str(e)}"

    return ""
