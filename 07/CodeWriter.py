"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


class CodeWriter:
    """Translates VM commands into Hack assembly code."""

    def __init__(self, output_stream: typing.TextIO) -> None:
        """Initializes the CodeWriter.

        Args:
            output_stream (typing.TextIO): output stream.
        """
        # Your code goes here!
        # Note that you can write to output_stream like so:
        # output_stream.write("Hello world! \n")
        self.outp_stream = output_stream
        self.counter_for_labels = 0
        self.counter_for_call = 0
        self.input_filename = ''
        self.current_function = ''
        self.outp_stream.write("@256\nD=A\n@SP\nM=D\n")
        self.segment_base_addresses = {"local": "LCL", "argument": "ARG", "this": "THIS", "that": "THAT"}


        self.arithmetic_dict = {
            "add":

                "//add\n@SP\n"
                "M=M-1\n"
                "A=M\n"
                "D=M\n"
                "@SP\n"
                "M=M-1\n"
                "A=M\n"
                "M=M+D\n"
                "@SP\n"
                "M=M+1\n",

            "sub":
                "//sub\n@SP\n"
                "M=M-1\n"
                "A=M\n"
                "D=M\n"
                "@SP\n"
                "M=M-1\n"
                "A=M\n"
                "M=M-D\n"
                "@SP\n"
                "M=M+1\n",

            "and":
                "//and\n@SP\n"
                "M=M-1\n"
                "A=M\n"
                "D=M\n"
                "@SP\n"
                "M=M-1\n"
                "A=M\n"
                "M=M&D\n"
                "@SP\n"
                "M=M+1\n",

            "or":
                "//or\n@SP\n"
                "M=M-1\n"
                "A=M\n"
                "D=M\n"
                "@SP\n"
                "M=M-1\n"
                "A=M\n"
                "M=M|D\n"
                "@SP\n"
                "M=M+1\n",

            "neg":
                "//neg\n"
                "@SP\n"
                "A=M-1\n"
                "M=-M\n",

            "not":
                "//not\n"
                "@SP\n"
                "A=M-1\n"
                "M=!M\n",

            "shiftleft":
                "//shiftleft\n"
                "@SP\n"
                "A=M-1\n"
                "M=M<<\n",

            "shiftright":
                "//shiftright\n"
                "@SP\n"
                "A=M-1\n"
                "M=M>>\n",
        }



    def set_file_name(self, filename: str) -> None:
        """Informs the code writer that the translation of a new VM file is 
        started.

        Args:
            filename (str): The name of the VM file.
        """
        # Your code goes here!
        # This function is useful when translating code that handles the
        # static segment. For example, in order to prevent collisions between two
        # .vm files which push/pop to the static segment, one can use the current
        # file's name in the assembly variable's name and thus differentiate between
        # static variables belonging to different files.
        # To avoid problems with Linux/Windows/MacOS differences with regards
        # to filenames and paths, you are advised to parse the filename in
        # the function "translate_file" in Main.py using python's os library,
        # For example, using code similar to:
        # input_filename, input_extension = os.path.splitext(os.path.basename(input_file.name))

        self.input_filename = filename.split("\\")[-1]
        # TODO: Change it to self.input_filename += ".vm"
        self.input_filename = self.input_filename.replace(".vm", "")

    def write_arithmetic(self, command: str) -> None:
        """Writes assembly code that is the translation of the given 
        arithmetic command. For the commands eq, lt, gt, you should correctly
        compare between all numbers our computer supports, and we define the
        value "true" to be -1, and "false" to be 0.

        Args:
            command (str): an arithmetic command.
        """
        # Your code goes here!

        if command in ["gt", "lt", "eq"]:
            self.counter_for_labels += 1
            if command == "gt":
                self.outp_stream.write("//gt\n"
                    "@SP\n"
                "M=M-1\n"
                "A=M\n"
                "D=M\n"  
                "@top\n"
                "M=D\n"
                "@SP\n"
                 "M=M-1\n"
                "A=M\n"
                "D=M\n"
                "@second\n"
                "M=D\n"
                "@top\n"
                "D=M\n"
                "@TOPNEG" + str(self.counter_for_labels) + "\n"
                "D;JLT\n"
                "@TOPPOSZERO" + str(self.counter_for_labels) + "\n"
                "0;JMP\n"                                                                                         
                "(TOPNEG"+str(self.counter_for_labels) + ")\n"
                "@second\n"
                "D=M\n"
                "@SAMESIGNORSECZERO" + str(self.counter_for_labels) + "\n"
                "D;JLE\n"
                "@TRUE" + str(self.counter_for_labels) + "\n"  # top<sec so true
                "0;JMP\n"
                "(TOPPOSZERO" + str(self.counter_for_labels) + ")\n"
                "@second\n"
                "D=M\n"
                "@SAMESIGNORSECZERO" + str(self.counter_for_labels) + "\n"
                "D;JGE\n"
                "D=0\n" # top>sec so false
                "@UPDATESP" + str(self.counter_for_labels) + "\n"  # jumps into update the sp after putting -1
                "0;JMP\n"
                "(SAMESIGNORSECZERO" + str(self.counter_for_labels) + ")\n"
                "@top\n"
                "D=M\n"
                "@second\n"
                "D=M-D\n"  # sec - top
                "@TRUE" + str(self.counter_for_labels) + "\n"  # sec>top so true
                "D;JGT\n"
                "D=0\n"
                "@UPDATESP" + str(self.counter_for_labels) + "\n"  # jumps into update the sp after putting -1
                "0;JMP\n"
                "(TRUE" + str(self.counter_for_labels) + ")\n"
                "D=-1\n"
                "@UPDATESP" + str(self.counter_for_labels) + "\n"  # jumps into update the sp after putting -1
                "0;JMP\n"
                "(UPDATESP" + str(self.counter_for_labels) + ")\n"
                "@SP\n"
                "A=M\n"
                "M=D\n"
                "@SP\n"
                "M=M+1\n")
            elif command == "lt":
                self.outp_stream.write("//lt\n"
                    "@SP\n"
                "M=M-1\n"
                "A=M\n"
                "D=M\n"  # VAL1
                "@top\n"
                "M=D\n"
                "@SP\n"
                "M=M-1\n"
                "A=M\n"
                "D=M\n"
                "@second\n"
                "M=D\n"
                "@top\n"
                "D=M\n"
                "@TOPNEG"+str(self.counter_for_labels) + "\n"
                "D;JLT\n"
                "@TOPPOSZERO"+str(self.counter_for_labels) +"\n"
                "0;JMP\n"                           
                "(TOPNEG"+str(self.counter_for_labels) + ")\n"
                "@second\n"
                "D=M\n"
                "@SAMESIGNORSECZERO"+str(self.counter_for_labels) + "\n"
                "D;JLE\n"                                              
                "D=0\n" #top<sec so false
                "@UPDATESP" + str(self.counter_for_labels) + "\n"  # jumps into update the sp after putting -1
                "0;JMP\n"            
                "(TOPPOSZERO"+str(self.counter_for_labels) +")\n"
                "@second\n"
                "D=M\n"
                "@SAMESIGNORSECZERO"+str(self.counter_for_labels) + "\n"
                "D;JGE\n"
                "@TRUE"+str(self.counter_for_labels) + "\n" #top>sec so true
                "0;JMP\n"
                "(SAMESIGNORSECZERO"+ str(self.counter_for_labels) + ")\n"
                "@top\n"
                "D=M\n"
                "@second\n"
                "D=M-D\n" #sec - top
                "@TRUE"+str(self.counter_for_labels) + "\n" #top>sec so true
                "D;JLT\n"
                "D=0\n"
                "@UPDATESP" + str(self.counter_for_labels) + "\n"  # jumps into update the sp after putting -1
                "0;JMP\n"
                "(TRUE" +str(self.counter_for_labels) +")\n"
                "D=-1\n"
                "@UPDATESP" + str(self.counter_for_labels) + "\n"  # jumps into update the sp after putting -1
                "0;JMP\n"
                "(UPDATESP" + str(self.counter_for_labels) + ")\n"
                "@SP\n"
                "A=M\n"
                "M=D\n"
                "@SP\n"
                "M=M+1\n")
            elif command == "eq":
                self.outp_stream.write("//eq\n"
                                       "@SP\n"
                "M=M-1\n"
                "A=M\n"
                "D=M\n"
                "@top\n"
                "M=D\n"
                "@SP\n"
                "M=M-1\n"
                "A=M\n"
                "D=M\n"
                "@second\n"
                "M=D\n"
                "@top\n"
                "D=M\n"
                "@TOPNEG" + str(self.counter_for_labels) + "\n"
                "D;JLT\n"
                "@TOPPOSZERO" + str(self.counter_for_labels) + "\n"
                "0;JMP\n"                                                                                        
                "(TOPNEG" + str(self.counter_for_labels) + ")\n"
                "@second\n"
                "D=M\n"
                "@SAMESIGNORSECZERO" + str(self.counter_for_labels) + "\n"
                "D;JLE\n"
                "D=0\n"  # top<sec so false
                "@UPDATESP" + str(self.counter_for_labels) + "\n"  # jumps into update the sp after putting -1
                "0;JMP\n"
                "(TOPPOSZERO" + str(self.counter_for_labels) + ")\n"
                "@second\n"
                "D=M\n"
                "@SAMESIGNORSECZERO" + str(self.counter_for_labels) + "\n"
                "D;JGE\n"
                "D=0\n"  # top>sec so false
                "@UPDATESP" + str(self.counter_for_labels) + "\n"  # jumps into update the sp after putting -1
                "0;JMP\n"
                "(SAMESIGNORSECZERO" + str(self.counter_for_labels) + ")\n"
                "@top\n"
                "D=M\n"
                "@second\n"
                "D=M-D\n"  # sec - top
                "@TRUE" + str(self.counter_for_labels) + "\n"  # sec==top so true
                "D;JEQ\n"
                "D=0\n"
                "@UPDATESP" + str(self.counter_for_labels) + "\n"  # jumps into update the sp after putting -1
                "0;JMP\n"
                "(TRUE" + str(self.counter_for_labels) + ")\n"
                "D=-1\n"
                "@UPDATESP" + str(self.counter_for_labels) + "\n"  # jumps into update the sp after putting -1
                "0;JMP\n"
                "(UPDATESP" + str(self.counter_for_labels) + ")\n"
                "@SP\n"
                "A=M\n"
                "M=D\n"
                "@SP\n"
                "M=M+1\n")
        else:
            self.outp_stream.write(self.arithmetic_dict[command])

    def write_push_pop(self, command: str, segment: str, index: int) -> None:
        """Writes assembly code that is the translation of the given
        command, where command is either C_PUSH or C_POP.

        Args:
            command (str): "C_PUSH" or "C_POP".
            segment (str): the memory segment to operate on.
            index (int): the index in the memory segment.
        """


        if command == "C_PUSH":
            if segment == "constant":
                self.outp_stream.write("//push constant " + str(index) + "\n" +
                                       "@" + str(index) + "\n" +
                                       "D=A\n" +
                                       "@SP\n" +
                                       "A=M\n" +
                                       "M=D\n" +
                                       "@SP\n" +
                                       "M=M+1\n")
            elif segment == "static":
                self.outp_stream.write("//push static " + str(index) + "\n" +
                                       "@"  + "." + str(index) + "\n" +
                                       "D=M\n" +
                                       "@SP\n" +
                                       "A=M\n" +
                                       "M=D\n" +
                                       "@SP\n" +
                                       "M=M+1\n")
            elif segment in ["local", "argument", "this", "that"]:
                self.outp_stream.write("//push " + segment + " " + str(index) + "\n" +
                                       "@" + self.segment_base_addresses[segment] + "\n" +
                                       "D=M\n" +
                                       "@" + str(index) + "\n" +
                                       "D=D+A\n" +
                                       "A=D\n" +
                                       "D=M\n" +
                                       "@SP\n" +
                                       "A=M\n" +
                                       "M=D\n" +
                                       "@SP\n" +
                                       "M=M+1\n")
            elif segment in ["temp", "pointer"]:
                offset = "5" if segment == "temp" else "3"
                self.outp_stream.write("//push " + segment + " " + str(index) + "\n" +
                                       "@" + str(index) + "\n" +
                                       "D=A\n" +
                                       "@" + offset + "\n" +
                                       "A=A+D\n" +
                                       "D=M\n" +
                                       "@SP\n" +
                                       "A=M\n" +
                                       "M=D\n" +
                                       "@SP\n" +
                                       "M=M+1\n")
        elif command == "C_POP":
            if segment == "static":
                self.outp_stream.write("//pop " + "." + str(index) + "\n" +
                                       "@SP\n" +
                                       "A=M-1\n" +
                                       "D=M\n" +
                                       "@" + "." + str(index) + "\n" +
                                       "M=D\n"+
                                       "@SP\n"+
                                       "M=M-1\n")
            elif segment in ["local", "argument", "this", "that"]:
                self.outp_stream.write("//pop " + segment + " " + str(index) + "\n" +
                                       "@" + self.segment_base_addresses[segment] + "\n" +
                                       "D=M\n" +
                                       "@" + str(index) + "\n" +
                                       "D=D+A\n" +
                                       "@R14\n" +
                                       "M=D\n" +
                                       "@SP\n" +
                                       "M=M-1\n" +
                                       "A=M\n" +
                                       "D=M\n" +
                                       "@R14\n" +
                                       "A=M\n" +
                                       "M=D\n")
            elif segment in ["temp", "pointer"]:
                offset = "5" if segment == "temp" else "3"
                self.outp_stream.write("//pop" + segment + " " + str(index) + "\n" +
                                       "@" + offset + "\n" +
                                       "D=A\n" +
                                       "@" + str(index) + "\n" +
                                       "D=D+A\n" +
                                       "@R14\n" +
                                       "M=D\n" +
                                       "@SP\n" +
                                       "M=M-1\n" +
                                       "A=M\n" +
                                       "D=M\n" +
                                       "@R14\n" +
                                       "A=M\n" +
                                       "M=D\n")

    # Assume output_stream and func are defined in the broader scope as before

    def write_assembly(instruction):
        """Utility function to write the given assembly instruction to the output stream."""
        output_stream.write(instruction + '\n')

    def write_label(self, label):
        """Writes assembly code for the label command."""
        label_name = self.current_function + "" + label
        write_assembly(f"// label {label}\n({label_name})")

    def write_goto(self, label):
        """Writes assembly code for the goto command."""
        label_name = self.current_function + "" + label
        write_assembly(f"// goto {label}\n@{label_name}\n0;JMP")

    def write_if(self, label):
        """Writes assembly code for the if-goto command."""
        label_name = self.current_function + "" + label
        write_assembly(f"// if-goto {label}\n@SP\nAM=M-1\nD=M\n@{label_name}\nD;JNE")

    def write_function(function_name, n_vars):
        """Writes assembly code for the function command."""
        self.current_function = function_name  # Update the function context
        instructions = [f"// function {function_name}\n({function_name})"]
        instructions += ["@SP\nA=M\nM=0\n@SP\nM=M+1" for _ in range(n_vars)]
        write_assembly('\n'.join(instructions))

    def write_init(self):
        self.write_call("Sys.init", 0)


    def write_call(self, function_name: str, n_args: int) -> None:
        """Writes assembly code that affects the call command.
        Let "Xxx.foo" be a function within the file Xxx.vm.
        The handling of each "call" command within Xxx.foo's code generates and
        injects a symbol "Xxx.fooret.i" into the assembly code stream, where
        "i" is a running integer (one such symbol is generated for each "call"
        command within "Xxx.foo").
        This symbol is used to mark the return address within the caller's
        code. In the subsequent assembly process, the assembler translates this
        symbol into the physical memory address of the command immediately
        following the "call" command.

        Args:
            function_name (str): the name of the function to call.
            n_args (int): the number of arguments of the function.
        """
        # This is irrelevant for project 7,
        # you will implement this in project 8!
        # The pseudo-code of "call function_name n_args" is:
        # push return_address   // generates a label and pushes it to the stack
        # push LCL              // saves LCL of the caller
        # push ARG              // saves ARG of the caller
        # push THIS             // saves THIS of the caller
        # push THAT             // saves THAT of the caller
        # ARG = SP-5-n_args     // repositions ARG
        # LCL = SP              // repositions LCL
        # goto function_name    // transfers control to the callee
        # (return_address)      // injects the return address label into the code

        return_address = f"{self.current_function}ret.{self.counter_for_call}"
        assembly_code = f"//call function\n"
        # Push return address
        assembly_code += f"@{return_address}\nD=A\n@SP\nA=M\nM=D\n@SP\nM=M+1\n"
        # Save caller's frame
        for segment in range(1, 5):
            assembly_code += f"@{segment}\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n"
        # Reposition ARG for callee
        assembly_code += "@SP\n" \
                     "D=M\n" \
                     "@5\n" \
                     "D=D-A\n" \
                     "@" + str(n_args) + \
                     "\nD=D-A\n" \
                     "@2\n" \
                     "M=D\n"\
                     "@SP\n" \
                     "D=M\n" \
                     "@1\n" \
                     "M=D\n"
        # Goto callee
        assembly_code += f"@{function_name}\n0;JMP\n"
        # Insert return address label
        assembly_code += f"({return_address})\n"

        self.outp_stream.write(assembly_code)
        self.counter_for_call += 1

    def assemble_return_procedure(self):
        """Generates assembly code for handling the VM 'return' command,
        following the VM semantics for returning from a function call."""
        # Generate a unique label for frame and return address calculations
        frame_label = "FRAME_VAR"
        ret_addr_label = "RETURN_ADDR"

        # Helper method to write the assembly for setting a temporary variable
        def set_temp_var(label, value):
            self.outp_stream.write(f"@{value}\nD=M\n@{label}\nM=D\n")

        # Helper method for restoring caller's context
        def restore_segment(segment, offset):
            self.outp_stream.write(f"@{frame_label}\nD=M\n@{offset}\nA=D-A\nD=M\n@{segment}\nM=D\n")

        # Set FRAME to LCL and calculate return address
        set_temp_var(frame_label, "LCL")
        self.outp_stream.write(f"@5\nA=D-A\nD=M\n@{ret_addr_label}\nM=D\n")

        # Reposition the return value for the caller
        self.outp_stream.write("@SP\nA=M-1\nD=M\n@ARG\nA=M\nM=D\n")

        # Restore SP of the caller
        self.outp_stream.write("@ARG\nD=M+1\n@SP\nM=D\n")

        # Restore THAT, THIS, ARG, LCL of the caller
        restore_segment("THAT", 1)
        restore_segment("THIS", 2)
        restore_segment("ARG", 3)
        restore_segment("LCL", 4)

        # Jump to return address
        self.outp_stream.write(f"@{ret_addr_label}\nA=M\n0;JMP\n")

        # Increment the return procedure counter (if exists) to ensure unique labels
        if hasattr(self, 'return_procedure_counter'):
            self.return_procedure_counter += 1
        else:
            self.return_procedure_counter = 1

    # Assuming the above function is defined within the same class as write_return
    def write_return(self):
        """Wrapper method that calls the refactored return handling assembly generator."""
        self.assemble_return_procedure()
