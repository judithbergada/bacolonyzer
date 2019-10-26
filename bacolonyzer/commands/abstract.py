import abc


class AbstractCommand:
    """Abstract class used to define shared logic for all commands in
    bacolonyzer."""

    # Name for the command.
    _SUBCOMMAND = None
    # Description of the subcommand shown in the help.
    _DESCRIPTION = None

    def register_parser(self, subparsers):
        # Register this class as a subcommand of the main bacolonyzer script.
        group = subparsers.add_parser(
            self._SUBCOMMAND,
            help=self._DESCRIPTION,
            description=self._DESCRIPTION)
        # Call the method of the class responsible for adding all arguments
        # given by the user.
        self.register_arguments(group)
        # Register the method `run()` to be called when a subcommand is called.
        group.set_defaults(func=self.run)

    @abc.abstractmethod
    def register_arguments(self, parser):
        """Register command arguments into the given parser."""

    @abc.abstractmethod
    def run(self, args):
        """Run command logic."""
