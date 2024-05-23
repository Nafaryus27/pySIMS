# pySIMS

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
cd PYSIMS_DIR
pip3 install .
```
