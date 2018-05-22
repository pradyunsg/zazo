class YAMLException(Exception):
    """Base for the exception hierarchy of this module
    """

    def __str__(self):
        # Format a reason
        if not self.args:
            message = "unknown"
        elif len(self.args) == 1:
            message = self.args[0]
        else:
            try:
                message = self.args[0].format(*self.args[1:])
            except Exception as error:
                message = "Unable to format message: {}\n{}".format(
                    self.args, error
                )
        # Print the reason
        return "YAML is malformed -- reason: {}".format(message)
