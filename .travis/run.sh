# We want to create the virtual environment here, but not actually run anything
tox --notest

# Run the unit tests
tox -- -m unit

# Run our integration tests
tox -- -m integration -n 8
