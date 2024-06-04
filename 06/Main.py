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
from SymbolTable import SymbolTable
from Parser import Parser
from Code import Code


def assemble_file(
        input_file: typing.TextIO, output_file: typing.TextIO) -> None:
    """Assembles a single file.

    Args:
        input_file (typing.TextIO): the file to assemble.
        output_file (typing.TextIO): writes all output to this file.
    """
    # Your code goes here!
    # A good place to start is to initialize a new Parser object:
    # parser = Parser(input_file)
    # Note that you can write to output_file like so:
    # output_file.write("Hello world! \n")

    parser = Parser(input_file)
    sym_table = SymbolTable()
    label_exist_counter = 0

    # loop until get rid of L commands  (first pass)
    while parser.has_more_commands():
        parser.current_line_index += 1
        parser.advance()
        if parser.current_command is not None:
            if parser.command_type() == "L_COMMAND":
                sym_table.add_entry(parser.symbol(), parser.current_line_index - label_exist_counter)
                label_exist_counter += 1

    # loop to fill the sym_table

    parser.current_line_index = -1

    while parser.has_more_commands():
        parser.current_line_index += 1
        parser.advance()
        if parser.current_command is not None:
            if parser.command_type() == "A_COMMAND":
                # handle numbers :
                if parser.symbol().isnumeric():
                    bin_num = bin(int(parser.symbol()))[2:].zfill(16)
                    output_file.write(bin_num)
                    output_file.write('\n')
                else:
                    if not sym_table.contains(parser.symbol()):
                        sym_table.add_entry(parser.symbol(), sym_table.sym_index)
                        sym_table.sym_index += 1
                    bin_num = bin(sym_table.get_address(parser.symbol()))[2:].zfill(16)
                    output_file.write(bin_num)
                    output_file.write('\n')

            elif parser.command_type() == "C_COMMAND":
                code = Code
                bin_num = is_shift_command(parser.current_command)
                if bin_num != "":
                    output_file.write(bin_num)
                    output_file.write('\n')
                    continue
                bin_num = "111"
                bin_num += code.comp(parser.comp())
                bin_num += code.dest(parser.dest())
                bin_num += code.jump(parser.jump())
                output_file.write(bin_num)
                output_file.write('\n')

    output_file.close()


def is_shift_command(command):
    if command == "D=D>>":
        return "1010010000010000"
    elif command == "D=D<<":
        return "1010110000010000"
    elif command == "D=A>>":
        return "1010000000010000"
    elif command == "D=A<<":
        return "1010100000010000"
    elif command == "D=M>>":
        return "1011000000010000"
    elif command == "D=M<<":
        return "1011100000010000"
    return ""


if "__main__" == __name__:
    # Parses the input path and calls assemble_file on each input file.
    # This opens both the input and the output files!
    # Both are closed automatically when the code finishes running.
    # If the output file does not exist, it is created automatically in the
    # correct path, using the correct filename.
    if not len(sys.argv) == 2:
        sys.exit("Invalid usage, please use: Assembler <input path>")
    argument_path = os.path.abspath(sys.argv[1])
    if os.path.isdir(argument_path):
        files_to_assemble = [
            os.path.join(argument_path, filename)
            for filename in os.listdir(argument_path)]
    else:
        files_to_assemble = [argument_path]
    for input_path in files_to_assemble:
        filename, extension = os.path.splitext(input_path)
        if extension.lower() != ".asm":
            continue
        output_path = filename + ".hack"
        with open(input_path, 'r') as input_file, \
                open(output_path, 'w') as output_file:
            assemble_file(input_file, output_file)
