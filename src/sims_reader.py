import json
from pprint import pprint
import tatsu

_str2float = lambda s: float(s or 0)

class Semantic:
    def __init__(self):
        pass

    def meta_section(self, ast):
        params = {param:ast.body.value[i] for i,param in enumerate(ast.body.param)}
        return params

    def data_section(self, ast):
        body = ast.body
        sample = body.sample
        raw_data = [list(map(_str2float, row)) for row in body.data]

        data_dict = dict()
        data_header = body.data_header
        for i,e in enumerate(body.table_header):
            elem = e[0]
            nb_columns = len(e[1])
            values = lambda j : [row[i+j] for row in raw_data]
            data_dict[elem] = {data_header[i+j]:values(j) for j in range(nb_columns)}
        return(data_dict)

        
        
        
def parse_with_semantic(data, grammar):
    parser = tatsu.compile(grammar)
    ast = parser.parse(data, semantics=Semantic())

    pprint(ast)
    
if __name__ == '__main__':

    with open('grammar.ebnf') as f:
        grammar = f.read()

    with open('../Data/E3SITEST84.nrj_rpc_txt', 'r', encoding="latin1") as f:
#    with open('../Data/D3GZ46.dp_rpc_txt', 'r', encoding="latin1") as f:
#    with open('../Data/D4GZ46.ms_rpc_txt', 'r', encoding="latin1") as f:
        data = f.read()
    
    parse_with_semantic(data, grammar)
