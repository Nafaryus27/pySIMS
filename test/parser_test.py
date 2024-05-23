from pysims.datamodel.sims_parser import Parser
from tatsu.util import asjson
import pytest
import json

#===========================Configuration============================#

# input test files
path_inputs = "./files/"
input_name = "input"
dp_input = path_inputs + input_name + ".dp"
ms_input = path_inputs + input_name + ".ms"
nrj_input = path_inputs + input_name + ".nrj"

# expected results files
path_expected = "./files/parser_grammar_output/"
expected_name = "expected"
dp_expected = path_expected + expected_name + "_dp.txt"
ms_expected = path_expected + expected_name + "_ms.txt"
nrj_expected = path_expected + expected_name + "_nrj.txt"

#=============================Unit Tests=============================#

def test_parser_dp():
    with open(dp_input, 'r', encoding='iso-8859-1') as f:
        data = f.read()
        
    with open(dp_expected, 'r', encoding='iso-8859-1') as f:
        expected = json.loads(f.read())

    parser = Parser()
    output = asjson(parser.parse(data))
    assert output == expected, "Test parser output on .dp format failed"
    

def test_parser_ms():
    with open(ms_input, 'r', encoding='iso-8859-1') as f:
        data = f.read()
        
    with open(ms_expected, 'r', encoding='iso-8859-1') as f:
        expected = json.loads(f.read())

    parser = Parser()
    output = asjson(parser.parse(data))
    assert output == expected, "Test parser output on .ms format failed"



def test_parser_nrj():
    with open(nrj_input, 'r', encoding='iso-8859-1') as f:
        data = f.read()
        
    with open(nrj_expected, 'r', encoding='iso-8859-1') as f:
        expected = json.loads(f.read())

    parser = Parser()
    output = asjson(parser.parse(data))
    assert output == expected, "Test parser output on .nrj format failed"

