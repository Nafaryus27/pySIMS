Parser and Grammar principles
=============================

The goal of a parser is to read and convert a file or input, in a well
defined format, to a coherent data structure which is easy to
manipulate and process.

One advantage of a parser is that it uses a grammar, which describes
how the input file is structured to read and break the file down in
elementary blocks, which can then be processed by the semantic, mainly
to reformat the input data in a more manageable data structure, while
keeping the coherency between the initial and output data. This also
helps detects if the input file is not in the correct format, if it
has been tampered with, or if the format evolved and we need to update
our grammar.

An other advantage is that the grammar is normally very human
readable, since it only describes how the file is structured, thus you
only have to read it through to understand it (supposing you raed
grammar the language documentation to understand the symbols).

The parser used for PySims is made with the TatSu python module and
the ebnf grammar format and the grammar is located in
``datamodel/grammar.ebnf``, along with the semantic in
``datamodel/semantic.py``.  See
https://tatsu.readthedocs.io/en/stable/syntax.html for mor infos.


For example, let's say we have to parse the following block of text ::

  *** ANALYSIS POSITION ***
  
  Data file name(s);name.dp
  Shuttle_ID;1_hole
  Stage coordinates
  X(um);-212
  Y(um);1327
  Z(um);0
  Window coordinates
  X(um);-212
  Y(um);326
  Sample coordinates
  X(um);-212
  Y(um);326
  
  *** ANALYSIS RECIPE ***
  
  File name(s);No_name_1.rdp
  Creation date;05/08/2023
  Creation time;12:09


We can see that there are two similar sections, made of a header, an
empty line, a body, and some empty lines. Thus we can define a
section in the grammar such as ::

 section
	=
 	section_header
	empty_line
	body
	empty_lines
	;

And now all we need to do is describe what is a ``section_header``, a
``body`` or an ``empty line`` etc

For example we could define the ``body`` to be ::

  body
      =
      { meta_subsection | line }+
      ;

Which reads as :

* ``{...}+`` : meta_body is a list of at leat one element 
* ``subsection | line`` : the elements of ``body`` can be either a ``line`` which we would need to describe, or a ``subsection``, if we consider ::
     
     Stage coordinates
     X(um);-212
     Y(um);1327
     Z(um);0
     
     Window coordinates
     X(um);-212
     Y(um);326

     Sample coordinates
     X(um);-212
     Y(um);326
     
  to be some sort of subsections, which we would also need to describe.

And by following this principle of trying to break down the input file
into the smallest block possible, like tiny lego piece, we can then
assemble them back together to describe complexe file structure and
assert that if the parser succeeds in parsing the input file, then the
extracted data is coherent to what is actually stored in the file.







