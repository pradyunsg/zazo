import os

import pytest


def pytest_collection_modifyitems(items):
    """Marks the tests as unit or integration depending on which folder they
    live in
    """
    for item in items:
        # We don't want to touch DoctestTextfile and others.
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
            raise RuntimeError(
                "Unknown test type (filename = {0}, root_dir = {1})".format(
                    module_path, module_root_dir
                )
            )
