class YAMLException(Exception):
    """Raised when a YAML test is not formatted correctly.
    """

    def __str__(self):
        # Format a reason
        if not self.args:
            reason = "unknown"
        elif len(self.args) == 1:
            reason = self.args[0]
        else:
            try:
                reason = self.args[0].format(*self.args[1:])
            except Exception as error:
                reason = "Unable to format message: {}\n{}".format(self.args, error)

        # Append the reason
        return "YAML is malformed -- reason: {}".format(reason)


class MalformedYAML(YAMLException):
    """Raised when a malformed YAML specification is found.
    """

    def __init__(self, test_id, message, *args, **kwargs):
        super(MalformedYAML, self).__init__()
        self.id = test_id
        self.message = message.format(*args, **kwargs)

    def __str__(self):
        return "Malformed YAML in {}: {}".format(self.id, self.message)


class AggregatedYAMLErrors(YAMLException):
    """Raised when there are multiple issues with the YAML specification.
    """

    def __init__(self):
        super(AggregatedYAMLErrors, self).__init__()
        self._errors = []

    def __bool__(self):
        return bool(self._errors)

    __nonzero__ = __bool__  # Python 2 stuff

    def add(self, error):
        if isinstance(error, AggregatedYAMLErrors):
            self._errors.extend(error._errors)
        else:
            self._errors.append(error)

    def __str__(self):
        if not self._errors:
            return "<no errors>"
        elif len(self._errors) == 1:
            return str(self._errors[0])
        else:
            parts = ["There are multiple issues:"]
            for err in self._errors:
                parts.append(str(err))
            return "\n- ".join(parts)
