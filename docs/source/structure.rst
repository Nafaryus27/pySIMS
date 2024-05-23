Introduction
============

PySims is a python module made facilitate anaylisis and porcessing of
Secondary Ions Mass Spectrometer analysis, by prodiving simple but
powerful processings tools, such as plateau detection and ideal
profile generation for depth profiles analysis, or comparison tools
between the mass spectrums and isotopes natural abundance.

It is made for CAMECA .ms, .dp and .nrj ascii file format.

Module Structure
================

The module is organized into one main module : ``pysims`` and several
submodules :

- ``datamodel`` : regroups everything related to the data structure. it
  contains in particular the grammar and semantic files for the parser
  and the ``Crater`` class definition, which is the base data class
  used to create the more advanced processings present in the other
  submodules.
- ``energy`` : groups the processings related to the energy spectrums
  analysis.
- ``mass`` : contains the processing related to the mass spectrums analysis. The
  processings are separated between ``massspectrum.py`` which contains
  the mains processing functions and ``isotopes.py`` which serves as a
  gateway to acces the data from the mendeleev module.
- ``multilayer`` : groups the processing of the depth profile analysis

The module also contains in internal ``utils`` submodule which holds
some constants used by the processing and in which we can also add
some utilitary functinos later on.

There is also a ``test`` folder containing unit tests to test the
parser grammar and semantic actions.
