"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import os
import sys
import typing
from Parser import Parser
from CodeWriter import CodeWriter


import typing

def translate_vm_instruction(parser, code_writer):
    """Utility function to translate a single VM instruction using the parser and code_writer."""
    command_type = parser.command_type()
    action_map = {
        "C_ARITHMETIC": lambda: code_writer.write_arithmetic(parser.arg1()),
        "C_PUSH": lambda: code_writer.write_push_pop(command_type, parser.arg1(), parser.arg2()),
        "C_POP": lambda: code_writer.write_push_pop(command_type, parser.arg1(), parser.arg2()),
        "C_LABEL": lambda: code_writer.write_label(parser.arg1()),
        "C_GOTO": lambda: code_writer.write_goto(parser.arg1()),
        "C_IF": lambda: code_writer.write_if(parser.arg1()),
        "C_FUNCTION": lambda: code_writer.write_function(parser.arg1(), parser.arg2()),
        "C_RETURN": lambda: code_writer.write_return(),
        "C_CALL": lambda: code_writer.write_call(parser.arg1(), parser.arg2()),
    }
    # Execute the corresponding function based on the command type
    if command_type in action_map:
        action_map[command_type]()

def translate_file(
        input_file: typing.TextIO, output_file: typing.TextIO,
        bootstrap: bool) -> None:

    """Translates a single VM file to Hack assembly.

    Args:
        input_file (typing.TextIO): VM file to translate.
        output_file (typing.TextIO): Destination for Hack assembly code.
        bootstrap (bool): If True, includes bootstrap code for VM initialization.
    """
    parser = Parser(input_file)
    code_writer = CodeWriter(output_file)

    if bootstrap:
        code_writer.write_initlizaiton()

    code_writer.set_file_name(input_file.name)

    # Translate each VM command to assembly
    while parser.has_more_commands():
        parser.current_line_index += 1
        parser.advance()
        translate_vm_instruction(parser, code_writer)


if "__main__" == __name__:
    # Parses the input path and calls translate_file on each input file.
    # This opens both the input and the output files!
    # Both are closed automatically when the code finishes running.
    # If the output file does not exist, it is created automatically in the
    # correct path, using the correct filename.
    if not len(sys.argv) == 2:
        sys.exit("Invalid usage, please use: VMtranslator <input path>")
    argument_path = os.path.abspath(sys.argv[1])
    if os.path.isdir(argument_path):
        files_to_translate = [
            os.path.join(argument_path, filename)
            for filename in os.listdir(argument_path)]
        output_path = os.path.join(argument_path, os.path.basename(
            argument_path))
    else:
        files_to_translate = [argument_path]
        output_path, extension = os.path.splitext(argument_path)
    output_path += ".asm"
    bootstrap = True
    with open(output_path, 'w') as output_file:
        for input_path in files_to_translate:
            filename, extension = os.path.splitext(input_path)
            if extension.lower() != ".vm":
                continue
            with open(input_path, 'r') as input_file:
                translate_file(input_file, output_file, bootstrap)
            bootstrap = False
