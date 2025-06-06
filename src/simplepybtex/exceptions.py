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


class PybtexError(Exception):
    def __init__(self, message, filename=None):
        super(PybtexError, self).__init__(message)
        self.filename = filename

    def get_context(self):  # pragma: no cover
        """Return extra error context info."""
        return None

    def get_filename(self):  # pragma: no cover
        """Return filename, if relevant."""
        if self.filename is None or isinstance(self.filename, str):
            return self.filename
        else:
            from .io import _decode_filename
            return _decode_filename(self.filename, errors='replace')

    def __eq__(self, other):
        return str(self) == str(other)

    def __hash__(self):  # pragma: no cover
        return hash(str(self))
