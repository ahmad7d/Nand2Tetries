"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


def removing_comments(input_lines):
    return [line.split('//')[0].replace(' ', '') for line in input_lines]


def removing_whitespaces(input_lines):
    return [line for line in input_lines if line != ""]


class Parser:
    """Encapsulates access to the input code. Reads an assembly program
    by reading each command line-by-line, parses the current command,
    and provides convenient access to the commands components (fields
    and symbols). In addition, removes all white space and comments.
    """

    def __init__(self, input_file: typing.TextIO) -> None:
        """Opens the input file and gets ready to parse it.

        Args:
            input_file (typing.TextIO): input file.
        """
        # Your code goes here!
        # A good place to start is to read all the lines of the input:
        # input_lines = input_file.read().splitlines()

        self.input_lines = input_file.read().splitlines()
        self.current_command = None
        self.current_line_index = -1

        self.input_lines = removing_comments(self.input_lines)
        self.input_lines = removing_whitespaces(self.input_lines)

    def has_more_commands(self) -> bool:
        """Are there more commands in the input?

        Returns:
            bool: True if there are more commands, False otherwise.
        """
        # Your code goes here!
        return self.current_line_index + 1 < len(self.input_lines)

    def advance(self) -> None:
        """Reads the next command from the input and makes it the current command.
        Should be called only if has_more_commands() is true.
        """
        self.current_command = self.input_lines[self.current_line_index]

    def is_A_command(self):
        return True if '@' in self.current_command else False

    def is_C_command(self):
        return True if '=' in self.current_command or ';' in self.current_command else False

    def is_L_command(self):
        return True if '(' in self.current_command and ')' in self.current_command else False

    def command_type(self) -> str:
        """
        Returns:
            str: the type of the current command:
            "A_COMMAND" for @Xxx where Xxx is either a symbol or a decimal number
            "C_COMMAND" for dest=comp;jump
            "L_COMMAND" (actually, pseudo-command) for (Xxx) where Xxx is a symbol
        """
        # Your code goes here!
        if self.is_A_command():
            return "A_COMMAND"
        if self.is_C_command():
            return "C_COMMAND"
        if self.is_L_command():
            return "L_COMMAND"

    def symbol(self) -> str:
        """
        Returns:
            str: the symbol or decimal Xxx of the current command @Xxx or
            (Xxx). Should be called only when command_type() is "A_COMMAND" or 
            "L_COMMAND".
        """
        # Your code goes here!

        # need to check if we can change the self.current_command or not
        symb = "null"
        if self.command_type() == "A_COMMAND":
            symb = self.current_command[1:]
        elif self.command_type() == "L_COMMAND":
            symb = self.current_command
            symb = symb.replace('(', '')
            symb = symb.replace(')', '')
        return symb

    def dest(self) -> str:
        """
        Returns:
            str: the dest mnemonic in the current C-command. Should be called 
            only when commandType() is "C_COMMAND".
        """
        # Your code goes here!

        if self.command_type() == "C_COMMAND":
            if self.current_command.find('=') != -1:
                return self.current_command[:self.current_command.find('=')]
            return "null"

    def comp(self) -> str:
        """
        Returns:
            str: the comp mnemonic in the current C-command. Should be called
            only when commandType() is "C_COMMAND".
        """
        # Your code goes here!

        if self.command_type() == "C_COMMAND":
            if self.current_command.find('=') != -1:
                return self.current_command[self.current_command.find('=') + 1:]
            if self.current_command.find(';') != -1:
                return self.current_command[:self.current_command.find(';')]

    def jump(self) -> str:
        """
        Returns:
            str: the jump mnemonic in the current C-command. Should be called 
            only when commandType() is "C_COMMAND".
        """
        # Your code goes here!

        if self.command_type() == "C_COMMAND":
            if self.current_command.find(';') == -1:
                return "null"
            else:
                return self.current_command[self.current_command.find(';') + 1:]
