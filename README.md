# aeroval_model_checker

Small tool for checking aerocom3 model data. Does not guarantee 100% that model files will work in pyaerocom, but it is a start...

## Installation

```
pip install git+https://github.com/metno/aeroval_model_checker
```

## Usage

```
aeroval_model_checker <model file location> [-v] [-s]
```

- `-v` for verbose output
- `-s` for stricter check. Might tell you that some variables are not supported. Variables with vmr(...) and conc(...) might be added to pyaerocom later, but might give error now

