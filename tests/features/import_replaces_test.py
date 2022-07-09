from __future__ import annotations

import pytest

from pyupgrade._data import Settings
from pyupgrade._main import _fix_plugins


@pytest.mark.parametrize(
    ('s', 'min_version'),
    (
        pytest.param('from a import b', (3,), id='unrelated import'),
        pytest.param(
            'from collections import Mapping\n',
            (2, 7),
            id='too old min version',
        ),
        pytest.param(
            'if True: from six.moves import getcwd, StringIO\n',
            (3,),
            id='play stupid games, win stupid prizes pt1',
        ),
        pytest.param(
            'if True:from six.moves import getcwd, StringIO\n',
            (3,),
            id='play stupid games, win stupid prizes pt2',
        ),
    ),
)
def test_import_replaces_noop(s, min_version):
    assert _fix_plugins(s, settings=Settings(min_version=min_version)) == s


@pytest.mark.parametrize(
    ('s', 'min_version', 'expected'),
    (
        pytest.param(
            'from collections import Mapping\n',
            (3,),
            'from collections.abc import Mapping\n',
            id='one-name replacement',
        ),
        pytest.param(
            'from collections import Mapping, Sequence\n',
            (3,),
            'from collections.abc import Mapping, Sequence\n',
            id='multi-name replacement',
        ),
        pytest.param(
            'from collections import Counter, Mapping\n',
            (3,),
            'from collections import Counter\n'
            'from collections.abc import Mapping\n',
            id='one name rewritten to new module',
        ),
        pytest.param(
            'from collections import Counter, Mapping, Sequence\n',
            (3,),
            'from collections import Counter\n'
            'from collections.abc import Mapping, Sequence\n',
            id='multiple names rewritten to new module',
        ),
        pytest.param(
            'from six.moves import getcwd, StringIO\n',
            (3,),
            'from io import StringIO\n'
            'from os import getcwd\n',
            id='all imports rewritten but to multiple modules',
        ),
        pytest.param(
            'from collections import Mapping as mapping, Counter\n',
            (3,),
            'from collections import Counter\n'
            'from collections.abc import Mapping as mapping\n',
            id='new import with aliased name',
        ),
        pytest.param(
            'if True:\n'
            '    from collections import Mapping, Counter\n',
            (3,),
            'if True:\n'
            '    from collections import Counter\n'
            '    from collections.abc import Mapping\n',
            id='indented import being added',
        ),
        pytest.param(
            'if True:\n'
            '    if True:\n'
            '        pass\n'
            '    from collections import Mapping, Counter\n',
            (3,),
            'if True:\n'
            '    if True:\n'
            '        pass\n'
            '    from collections import Counter\n'
            '    from collections.abc import Mapping\n',
            id='indented import after dedent',
        ),
        pytest.param(
            'if True: from collections import Mapping\n',
            (3,),
            'if True: from collections.abc import Mapping\n',
            id='inline import, only one replacement',
        ),
        pytest.param(
            'import os\n'
            'from collections import Counter, Mapping\n'
            'import sys\n',
            (3,),
            'import os\n'
            'from collections import Counter\n'
            'from collections.abc import Mapping\n'
            'import sys\n',
            id='other imports left alone',
        ),
    ),
)
def test_import_replaces(s, min_version, expected):
    ret = _fix_plugins(s, settings=Settings(min_version=min_version))
    assert ret == expected
