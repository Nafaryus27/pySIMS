# pySIMS

# Installation (Linux):
```
git clone https://github.com/Nafaryus27/pySIMS.git
cd pySIMS
python -m venv venv
source ./venv/bin/activate
pip3 install -r requirements.txt
cd src/pysims/datamodel
python -m tatsu grammar.ebnf --generate-parser --outfile sims_parser.py
cd src/pysims
pip3 install .
```
