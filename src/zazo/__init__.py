"""A Dependency Resolver written in Python
"""

__version__ = "0.1.0.dev0"

# Exit codes
SUCCESS = 0
if False:
    from typing import Text


def get_message():
    # type: () -> Text
    """Returns a message that would be printed by main()
    """
    return "Hello World!"


def main():
    # type: () -> int
    print(get_message())
    return SUCCESS


if __name__ == '__main__':
    import sys
    sys.exit(main())
