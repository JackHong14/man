import pytest
from man.manconfig import Version


@pytest.fixture
def version():
    return Version(1, 2, 4)


def test_version_revert(version: Version):
    with version:
        version[version.PATCH] = 18
        version[version.MINOR] = 42
        version[version.MAJOR] = 123

        assert version.last.version == [1, 2, 4]
        assert isinstance(version.last, Version)

    assert version.version == [1, 2, 4]
    assert version.last is None


def test_version_donot_revert(version: Version):
    with version:
        version[version.MINOR] = 42

        version.need_revert = False

    assert version[version.MINOR] == 42


def test_version_revert_callback(version: Version):
    def revert():
        raise RuntimeError

    with pytest.raises(RuntimeError):
        with version:
            version.revert_version = revert

    assert version.revert_version is not None

    def revert():
        assert 0 == 1

    with version:
        version.revert_version = revert
        version.need_revert = False


def test_version_setitem_by_name(version: Version):
    version['patch'] = 0
    assert version[version.PATCH] == 0

    version['Patch'] = 1
    assert version[version.PATCH] == 1

    version['paTcH'] = 2
    assert version[version.PATCH] == 2

    version['mInOr'] = 3
    assert version[version.MINOR] == 3

    version['MaJoR'] = 4
    assert version[version.MAJOR] == 4


def test_version_constants(version: Version):
    assert version.MAJOR == 0
    assert version.MINOR == 1
    assert version.PATCH == 2


def test_version_setitem_resets_lower_importance(version: Version):
    version[version.PATCH] = 100
    assert version.version == [1, 2, 100]

    version[version.MINOR] = 100
    assert version.version == [1, 100, 0]

    version[version.MAJOR] = 100
    assert version.version == [100, 0, 0]
