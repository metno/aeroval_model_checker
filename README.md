# aeroval_model_checker

Small tool for checking aerocom3 model data. Does not guarantee 100% that model files will work in pyaerocom, but it is a start...

The checker is run on a folder containing the model files, and checks if

1. The file names have the correct format
2. If the files can be read by xarray, and if they contain the correct dimentions
3. Checks if the varibale names in the files and in the file names match
4. Check if the files can be read by pyAerocom
## Requirements

Python >= 3.11
## Installation

```
pip install git+https://github.com/metno/aeroval_model_checker
```

## Usage

```
aeroval_model_checker <folder with model files> [-v] [-s]
```

- `-v` for verbose output
- `-s` for stricter check. Might tell you that some variables are not supported. Variables with vmr(...) and conc(...) might be added to pyaerocom later, but might give error now

