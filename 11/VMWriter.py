import typing

class VMWriter:
    """
    Writes VM commands into a file, encapsulating the syntax of VM commands.
    """

    def __init__(self, destination: typing.TextIO) -> None:
        """Initializes a VMWriter instance for writing VM commands to a file."""
        self.destination_stream = destination
        self.segment_mapping = {
            "LOCAL": "local", "CONST": "constant", "ARG": "argument",
            "STATIC": "static", "THIS": "this", "THAT": "that",
            "POINTER": "pointer", "TEMP": "temp"
        }
        self.arithmetic_ops = {
            "ADD": "add", "SUB": "sub", "NEG": "neg", "EQ": "eq",
            "GT": "gt", "LT": "lt", "AND": "and", "OR": "or", "NOT": "not",
            "SHIFTLEFT": "<<", "SHIFTRIGHT": ">>"
        }

    def _write_command(self, command: str, arg1: str = "", arg2: int = None) -> None:
        """Utility function to write a VM command to the destination file."""
        args = [arg1, str(arg2)] if arg2 is not None else [arg1]
        line = f"{command} {' '.join(filter(bool, args))}\n" if arg1 else f"{command}{' '.join(filter(bool, args))}\n"
        self.destination_stream.write(line)

    def write_push(self, segment: str, index: int) -> None:
        """Writes a VM push command."""
        self._write_command("push", self.segment_mapping.get(segment, segment), index)

    def write_pop(self, segment: str, index: int) -> None:
        """Writes a VM pop command."""
        self._write_command("pop", self.segment_mapping.get(segment, segment), index)

    def write_arithmetic(self, operation: str) -> None:
        """Writes a VM arithmetic command."""
        cmd = self.arithmetic_ops.get(operation.upper(), operation.lower())
        self._write_command(cmd)

    def write_label(self, label: str) -> None:
        """Writes a VM label command."""
        self._write_command("label", label)

    def write_goto(self, destination: str) -> None:
        """Writes a VM goto command."""
        self._write_command("goto", destination)

    def write_if(self, condition: str) -> None:
        """Writes a VM if-goto command."""
        self._write_command("if-goto", condition)

    def write_call(self, function_name: str, num_args: int) -> None:
        """Writes a VM call command."""
        self._write_command("call", function_name, num_args)

    def write_function(self, function_name: str, num_locals: int) -> None:
        """Writes a VM function command."""
        self._write_command("function", function_name, num_locals)

    def write_return(self) -> None:
        """Writes a VM return command."""
        self._write_command("return")
