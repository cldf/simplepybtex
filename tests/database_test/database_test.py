# Copyright (c) 2006-2021  Andrey Golovizin
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import pickle
from abc import ABCMeta, abstractmethod
from copy import deepcopy
from io import BytesIO, TextIOWrapper

import pytest
from simplepybtex.database import parse_bytes, parse_string, BibliographyData, Entry

from .data import reference_data


class DatabaseIO(object):
    __metaclass__ = ABCMeta

    def __init__(self):
        self.reference_data = deepcopy(reference_data)
        assert reference_data.entries
        assert reference_data.preamble

    @abstractmethod
    def serialize(self, bib_data):  # pragma: no cover
        pass

    @abstractmethod
    def deserialize(self, bib_data):  # pragma: no cover
        pass


class PybtexDatabaseIO(DatabaseIO):
    def __init__(self, bib_format):
        from simplepybtex.database.output.bibtex import Writer
        from simplepybtex.database.input.bibtex import Parser
        super(PybtexDatabaseIO, self).__init__()
        self.bib_format = bib_format
        self.writer = Writer(encoding='UTF-8')
        self.parser = Parser(encoding='UTF-8')

        if bib_format == 'bibtexml':
            # BibTeXML does not support TeX preambles
            self.reference_data._preamble = []

    def __repr__(self):  # pragma: no cover
        return '{}({!r})'.format(type(self).__name__, self.bib_format)


class PybtexStringIO(PybtexDatabaseIO):
    def serialize(self, bib_data):
        result = bib_data.to_string(self.bib_format)
        assert isinstance(result, str)
        return result

    def deserialize(self, string):
        # wrapper for parse_string
        return BibliographyData.from_string(string, self.bib_format)


class PybtexEntryStringIO(PybtexDatabaseIO):
    # the first entry in reference_data
    def __init__(self, bib_format):
        super(PybtexEntryStringIO, self).__init__(bib_format)
        # get 1st key
        self.key = list(reference_data.entries.keys())[0]
        # make Entry as single-item BibliographyData
        self.reference_data = reference_data.entries[self.key]
        assert reference_data.entries
        assert reference_data.preamble

    def serialize(self, bib_data):  # Entry.to_string
        result = bib_data.to_string(self.bib_format)
        assert isinstance(result, str)
        return result

    def deserialize(self, string):  # Entry.from_string
        return Entry.from_string(string, self.bib_format)


class PybtexBytesIO(PybtexDatabaseIO):
    def serialize(self, bib_data):
        result = bib_data.to_bytes(self.bib_format)
        assert isinstance(result, bytes)
        return result

    def deserialize(self, string):
        return parse_bytes(string, self.bib_format)


class PickleIO(DatabaseIO):
    def __init__(self, protocol):
        super(PickleIO, self).__init__()
        self.protocol = protocol

    def __repr__(self):  # pragma: no cover
        return '{}(protocol={!r})'.format(type(self).__name__, self.protocol)

    def serialize(self, bib_data):
        return pickle.dumps(bib_data, protocol=self.protocol)

    def deserialize(self, pickled_data):
        return pickle.loads(pickled_data)


class ReprEvalIO(DatabaseIO):
    def __repr__(self):  # pragma: no cover
        return '{}()'.format(type(self).__name__)

    def serialize(self, bib_data):
        return repr(bib_data)

    def deserialize(self, repr_value):
        from simplepybtex.utils import OrderedCaseInsensitiveDict
        from simplepybtex.database import BibliographyData, Entry, Person
        return eval(repr_value, {
            'OrderedCaseInsensitiveDict': OrderedCaseInsensitiveDict,
            'BibliographyData': BibliographyData,
            'Entry': Entry,
            'Person': Person,
        })


def check_database_io(io_obj):
    serialized_data = io_obj.serialize(io_obj.reference_data)
    deserialized_data = io_obj.deserialize(serialized_data)
    assert deserialized_data == io_obj.reference_data


@pytest.mark.parametrize(["io_cls"], [(PybtexBytesIO,), (PybtexStringIO,), (PybtexEntryStringIO,),(PybtexBytesIO,)])
@pytest.mark.parametrize(["bib_format"], [("bibtex",), ("bibtexml",), ("yaml",)])
def test_database_io(io_cls, bib_format):
    check_database_io(io_cls(bib_format))


@pytest.mark.parametrize(
    ["protocol"],
    [(protocol,) for protocol in range(0, pickle.HIGHEST_PROTOCOL + 1)]
)
def test_database_pickling(protocol):
    check_database_io(PickleIO(protocol))


def test_database_repr():
    check_database_io(ReprEvalIO())
