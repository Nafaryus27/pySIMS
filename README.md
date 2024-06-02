# pySIMS

## Includes :
- Loading and reading of depth profiles, mass spectrums, or energy spectrums profiles (CAMECA .dp, .ms, .nrj ascii files format). This gives acces to data and metadata  
- Depth profiles interfaces and plateaux detections for mutlilayers analysis.
- Ideal profiles géneration based on the detected interfaces and plateau values.
- Local maximum detection for mass spectrums peaks detections.
- Mass spectrum deviation to natural abundance for species caracterisation/detection.   

# Documentation :
Currently not integrated on github.
You can generate it manually by executing the following commands in `pySIMS` folder :
```
cd docs/
make html
```
And opening the generated `index.html` in `docs/build/html/`

# Installation (Linux):

Requires python >= 3.11

```
git clone https://github.com/Nafaryus27/pySIMS.git
cd pySIMS
PYSIMS_DIR=$(pwd)
python3.11 -m venv venv
source ./venv/bin/activate
pip3 install -r requirements.txt
cd src/pysims/datamodel
python3 -m tatsu grammar.ebnf --generate-parser --outfile sims_parser.py
cd $PYSIMS_DIR
pip3 install .
```
