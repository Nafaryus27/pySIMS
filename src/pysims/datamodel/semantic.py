def _str2float(s: str) -> float:
    return float(s or 0)


class Semantic:
    def __init__(self):
        pass

    def meta_section_line(self, ast):
        return [ast.param, ast.value]

    def meta_subsection(self, ast):
        return (ast.name, dict(ast.lines))

    def meta_section(self, ast):
        params = dict(ast.body.lines)
        if ast.body.subsections:
            subsections = dict(ast.body.subsections)
            params.update(subsections)
        return params

    def calib_species_subsection(self, ast):
        return [ast.name, dict(ast.params)]

    def calib_param_section(self, ast):
        section_name = ast.header.lower()
        params = dict(ast.body.lines)
        species = {section_name: dict(ast.body.species)}
        params.update(species)
        return params

    def meta_csv_section(self, ast):
        section_name = ast.header.section_name.lower()
        data = ast.data
        return {section_name: data}

    def data_section(self, ast):
        body = ast.body
        raw_data = [list(map(_str2float, row)) for row in body.data]

        data_dict = dict()
        data_header = body.data_header
        for i, e in enumerate(body.table_header):
            elem = e[0]
            nb_columns = len(e[1])
            values = lambda j: [row[i*nb_columns + j] for row in raw_data]
            data_dict[elem] = {data_header[i*nb_columns + j]: values(j) for j in range(nb_columns)}
        return data_dict

    def start(self, ast):
        sections = ast.sections
        metadata = {}
        data = {}
        for section in sections:
            if "metadata" in section:
                metadata.update(section["metadata"])
            if "data" in section:
                data.update(section["data"])
        return {"data": data, "metadata": metadata}
