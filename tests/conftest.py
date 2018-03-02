import os

import pytest

from tests.lib.yaml.fixtures import YamlFixtureFile


def pytest_collect_file(parent, path):
    if path.ext == ".yaml" and ".ignore" not in str(path):
        return YamlFixtureFile(path, parent)


def pytest_collection_modifyitems(session, config, items):
    # Mark Tests based on which directory they live in
    for item in items:
        if isinstance(item, YamlFixtureFile):
            item.add_marker(pytest.mark.yaml)
            item.add_marker(pytest.mark.integration)

        if not hasattr(item, 'module'):
            continue

        # Get path of the file
        module_path = os.path.relpath(
            item.module.__file__,
            os.path.commonprefix([__file__, item.module.__file__]),
        )
        # Mark the type of test
        module_root_dir = module_path.split(os.pathsep)[0]
        if module_root_dir.startswith("integration"):
            item.add_marker(pytest.mark.integration)
        elif module_root_dir.startswith("unit"):
            item.add_marker(pytest.mark.unit)
        else:
            msg = "Unknown test type (filename = {0}, root_dir = {1})".format(
                module_path, module_root_dir
            )
            raise RuntimeError(msg)
