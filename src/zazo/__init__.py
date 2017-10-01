"""A Dependency resolver written in pure Python
"""

__version__ = "0.1.0.dev0"

# Exit codes
SUCCESS = 0


def get_message():
    """Returns a message that would be printed by main()
    """
    # type: () -> Text
    return "Hello World!"


def main():
    # type: () -> int
    print(get_message())
    return SUCCESS


if __name__ == '__main__':
    import sys
    sys.exit(main())
