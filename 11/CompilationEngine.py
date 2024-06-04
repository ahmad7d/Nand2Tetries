
from JackTokenizer import JackTokenizer
from SymbolTable import SymbolTable
from VMWriter import VMWriter


class CompilationEngine:
    def __init__(self, token_stream: JackTokenizer, output_stream) -> None:
        """Initializes the compiler with a token stream for parsing."""
        self.tokenizer = JackTokenizer(token_stream)
        self.vm = VMWriter(output_stream)
        self.symbols = SymbolTable()
        self.labelCounter = 1
        self.className = ""

    def currentToken(self):
        """Advances to the next token if available, abstracting stream navigation."""
        return self.tokenizer.tokens[self.tokenizer.token_counter]

    def getNextToken(self):
        """Advances to the next token if available, abstracting stream navigation."""
        return self.tokenizer.tokens[self.tokenizer.token_counter + 1]

    def moveToNextToken(self):
        """Advances to the next token if available, abstracting stream navigation."""
        self.tokenizer.advance()

    def classCompile(self):
        """Orchestrates the compilation of a class from the token stream."""

        self.moveToNextToken()  # Begin class definition compilation
        self.className = self.get_identifier()  # Capture the class name
        self.moveToNextToken()  # Move past the class name
        self.moveToNextToken()  # Move past the class name

        # Handle class variable declarations
        while self.is_class_var_declaration():
            self.handle_class_variable_declaration()

        # Handle subroutine declarations
        while self.is_subroutine_declaration():
            self.compile_subroutine()

        self.moveToNextToken()  # Conclude class compilation

    def is_class_var_declaration(self):
        """Checks if the current token initiates a class variable declaration."""
        keyword = self.tokenizer.keyword().lower()
        return keyword in ["static", "field"]

    def is_subroutine_declaration(self):
        """Determines if the current token starts a subroutine declaration."""
        return self.tokenizer.keyword() in ["METHOD", "FUNCTION", "CONSTRUCTOR"]

    def get_identifier(self):
        """Retrieves the identifier from the current token."""
        return self.tokenizer.identifier()

    def handle_class_variable_declaration(self):
        """Compiles a static or a field declaration into the symbol table."""
        variable_kind = self.tokenizer.keyword().lower()  # Either 'static' or 'field'
        self.moveToNextToken()  # Move to variable type

        variable_type = self.determine_variable_type()  # Extract the type of the variable
        self.moveToNextToken()  # Move to variable type
        variable_name = self.get_identifier()  # Extract the first variable name
        self.moveToNextToken()  # Move to variable type

        self.register_variable(variable_name, variable_type, variable_kind.upper())

        # Handle multiple variable declarations in a single line
        while not self.current_token_equals(";"):
            self.moveToNextToken()  # Skip over the comma
            variable_name = self.get_identifier()  # Extract the next variable name
            self.moveToNextToken()  # Skip over the comma
            self.register_variable(variable_name, variable_type, variable_kind.upper())

        self.moveToNextToken()  # Move past the semicolon to conclude the variable declaration

    def determine_variable_type(self) -> str:
        """Determines and returns the type of a variable (e.g., int, char, boolean, class type)."""
        if self.tokenizer.token_type() == "KEYWORD":
            return self.tokenizer.keyword().lower()  # Primitive type
        else:
            return self.currentToken()  # Custom class type

    def current_token_equals(self, symbol: str) -> bool:
        """Checks if the current token matches the given symbol."""
        return self.tokenizer.symbol() == symbol

    def register_variable(self, name: str, var_type: str, kind: str):
        """Registers a variable in the symbol table."""
        self.symbols.define(name, var_type, kind)

    def compile_subroutine(self):
        """Compiles a method, function, or constructor."""
        self.symbols.start_subroutine()  # Reset subroutine-level symbols
        subroutine_kind = self.tokenizer.keyword().lower()  # Method, function, or constructor
        self.moveToNextToken()  # Move past the subroutine type


        # if self.tokenizer.token_type() == "KEYWORD":  # return val
        #     returnedVal = self.tokenizer.keyword().lower()

        # Skip the return type (not used directly in VM output but necessary for analysis)
        self.moveToNextToken()

        subroutine_name = self.get_identifier()  # Get the subroutine name
        self.moveToNextToken()  # Move past the subroutine name
        self.moveToNextToken()  # Move past the subroutine name

        if subroutine_kind == "method":
            self.symbols.define("this", self.className, "ARG")

        self.getParameters()  # Compile the parameter list
        self.moveToNextToken()  # Move past the subroutine name (get throught ')')


        # Prepare the VMWriter for subroutine declaration
        local_variables_count = self.compile_subroutine_body(subroutine_name, subroutine_kind)

        # VM command for function declaration
        # self.vm_write_function_declaration(subroutine_name, local_variables_count, subroutine_kind)

    def getParameters(self):
        """Compiles a (possibly empty) parameter list, excluding the enclosing '()'. """
        while not self.reached_end_of_parameter_list():
            param_type = self.determine_parameter_type()  # Retrieve the type of the parameter
            param_name = self.tokenizer.identifier()  # Extract parameter name
            self.symbols.define(param_name, param_type, "ARG")  # Register parameter in symbol table

            self.advance_through_token_stream()  # Move to the next token, could be ',' or ')'
            if self.tokenizer.current_token() == ",":
                self.skip_comma()  # Skip over the ',' to process the next parameter

    def reached_end_of_parameter_list(self):
        """Checks if the current token is the closing parenthesis marking the end of the parameter list."""
        return self.tokenizer.current_token() == ")"

    def determine_parameter_type(self):
        """Determines and returns the type of a parameter."""
        if self.tokenizer.token_type() == "KEYWORD":
            param_type = self.tokenizer.keyword().lower()  # Primitive type: int, char, boolean
        else:
            param_type = self.tokenizer.identifier()  # Class type
        self.tokenizer.advance()  # Advance past the type to the parameter name
        return param_type

    def advance_through_token_stream(self):
        """Advances the tokenizer, preparing to read the next parameter or end the parameter list."""
        self.moveToNextToken()

    def skip_comma(self):
        """Skips the comma between parameters in the list."""
        self.moveToNextToken()

    def compile_subroutine_body(self, subroutine_name: str, subroutine_kind: str) -> int:
        """Compiles the body of a subroutine, returning the count of local variables."""
        self.moveToNextToken()  # Advance past the opening '{' of the subroutine body

        # Initialize local variable count and compile all variable declarations at the start of the subroutine body
        local_variables_count = 0
        while self.currentToken() == "var":
            local_variables_count += self.compileVariableDeclarations()

        # VM function declaration
        self.vm.write_function(f"{self.className}.{subroutine_name}", local_variables_count)

        # Additional setup for methods
        if subroutine_kind == "method":
            self.vm.write_push("ARG", 0)
            self.vm.write_pop("POINTER", 0)

        # Additional setup for constructors
        if subroutine_kind == "constructor":
            fields_count = self.symbols.var_count("FIELD")
            self.vm.write_push("CONST", fields_count)
            self.vm.write_call("Memory.alloc", 1)
            self.vm.write_pop("POINTER", 0)

        # Compile statements within the subroutine body
        self.processStatements()

        self.moveToNextToken()  # Consume the closing '}'
        return local_variables_count

    def compileVariableDeclarations(self) -> int:
        """Compiles variable declarations, counting the number of variables declared."""
        declaredVariablesCount = 0
        self.moveToNextToken()  # Move past the 'var' keyword.
        variableType = self.currentTokenType()  # Retrieve the variable's type.

        while True:
            self.moveToNextToken()  # Move to variable name or ',' or ';'.
            if self.currentToken() == ";":
                break  # End of variable declaration statement.

            if self.currentToken() == ",":
                self.moveToNextToken()  # Skip ',' to move to the next variable name.

            variableName = self.tokenizer.identifier()  # Extract variable name.
            self.registerVariable(variableName, variableType, "VAR")  # Register variable in the symbol table.
            declaredVariablesCount += 1

        self.moveToNextToken()  # Move past ';' to the next statement or variable declaration.
        return declaredVariablesCount

    def currentTokenType(self):
        """Determines and returns the type of the current token."""
        if self.tokenizer.token_type() == "KEYWORD":
            return self.tokenizer.keyword().lower()  # For basic types like 'int', 'char', etc.
        else:
            # Handle custom class types.
            return self.currentToken()  # Assuming this method gets the full current token.

    def registerVariable(self, name: str, varType: str, kind: str):
        """Registers a variable in the symbol table with its name, type, and kind."""
        self.symbols.define(name, varType, kind)

    def processStatements(self):
        """Compiles a sequence of statements."""
        validStatements = {"while", "if", "return", "let", "do"}
        while self.currentToken() in validStatements:
            keywordAction = self.tokenizer.keyword()
            if keywordAction == "LET":
                self.handleLetStatement()
            elif keywordAction == "WHILE":
                self.handleWhileLoop()
            elif keywordAction == "IF":
                self.handleIfStatement()
            elif keywordAction == "DO":
                self.handleDoStatement()
            elif keywordAction == "RETURN":
                self.handleReturnStatement()



    def handleDoStatement(self) -> None:
        """Compiles a do statement."""
        self.moveToNextToken()
        self.evaluateExpression()
        self.moveToNextToken()
        self.vm.write_pop("TEMP", 0)

    def handleWhileLoop(self):
        """Processes a while loop, including its condition and body."""
        self.moveToNextToken()  # Skip 'while'
        self.moveToNextToken()
        startLoopLabel = f"LABEL{self.labelCounter}"
        self.labelCounter += 1


        # Mark the start of the loop
        self.vm.write_label(startLoopLabel)

        # Compile the loop condition
        self.evaluateExpression()
        # Negate the condition because 'if-goto' is used to exit the loop if the condition is false
        self.vm.write_arithmetic("NOT")

        self.moveToNextToken()
        self.moveToNextToken()

        endLoopLabel = f"LABEL{self.labelCounter}"
        self.labelCounter += 1

        # If the condition is false, exit the loop
        self.vm.write_if(endLoopLabel)

        # Compile the loop body
        self.processStatements()
        self.moveToNextToken()

        # Loop back to the start if the condition is true
        self.vm.write_goto(startLoopLabel)

        # Mark the end of the loop where execution continues if the condition is false
        self.vm.write_label(endLoopLabel)

    def handleIfStatement(self):
        """Compiles an if statement with an optional else clause."""
        self.moveToNextToken()  # Advance past 'if'
        self.moveToNextToken()  # Advance past '(' to the condition

        # Compile the condition expression
        self.evaluateExpression()

        self.moveToNextToken()
        self.moveToNextToken()

        self.vm.write_arithmetic("NOT")

        firstIfLabel = "LABEL" + str(self.labelCounter)
        self.vm.write_if(firstIfLabel)

        self.labelCounter += 1

        self.processStatements()
        self.moveToNextToken()

        secondIfLabel = "LABEL" + str(self.labelCounter)

        # Jump to false branch if condition is not met
        self.vm.write_goto(secondIfLabel)
        self.labelCounter += 1
        self.vm.write_label(firstIfLabel)


        # Check for an else clause and compile it
        if self.tokenizer.keyword() == "ELSE":
            self.moveToNextToken()  # Skip 'else'
            self.moveToNextToken()  # Skip '{'
            self.processStatements()
            self.moveToNextToken()  # Advance past the closing '}'

        # Mark the end of the if-else structure
        self.vm.write_label(secondIfLabel)

    def handleReturnStatement(self):
        """Processes a return statement, emitting VM commands."""
        self.moveToNextToken()  # Advance past 'return'
        # Check if the return statement is immediately followed by a semicolon, indicating a void return
        if self.currentToken() == ";":
            self.moveToNextToken()
            self.vm.write_push("CONST", 0)  # Push 0 for void return
            self.vm.write_return()
        else:
            # Otherwise, compile the return expression
            self.evaluateExpression()
            self.moveToNextToken()
            self.vm.write_return()


    def handleLetStatement(self):
        """Processes a let statement for variable assignment or array element update."""
        self.moveToNextToken()  # Advance past 'let'
        variableName = self.tokenizer.identifier()  # Retrieve the variable name
        self.moveToNextToken()  # Move to possibly '[' or '='

        # Check for array access
        isArrayAccess = False
        if self.currentToken() == "[":
            isArrayAccess = True
            self.handleArrayAssignmentPreparation(variableName)

        # Evaluate the right-hand side expression
        self.moveToNextToken()  # Move past '[' or '=' to the start of the expression
        self.evaluateExpression()
        self.moveToNextToken()
        # Complete the assignment based on whether it's a simple variable or an array element
        if not isArrayAccess:
            self.vm.write_pop(self.symbols.kind_of(variableName), self.symbols.index_of(variableName))
        else:
            self.completeArrayElementAssignment()

    def handleArrayAssignmentPreparation(self, variableName: str):
        """Prepares for an array element assignment by evaluating the index expression and adding it to the base address."""
        self.moveToNextToken()  # Move past '['
        # TODO: implement new method to get kind and indexOf
        self.vm.write_push(self.symbols.kind_of(variableName),
                           self.symbols.index_of(variableName))  # Push base address
        self.evaluateExpression()  # Evaluate index expression
        self.vm.write_arithmetic("ADD")  # Add base address and index
        self.moveToNextToken()  # Move past ']' to '='

    def completeArrayElementAssignment(self):
        """Completes the assignment to an array element after evaluating the right-hand side expression."""
        # The right-hand side expression value is now on top of the stack
        self.vm.write_pop("TEMP", 0)  # Temporarily store the value
        self.vm.write_pop("POINTER", 1)  # Set THAT to the computed address
        self.vm.write_push("TEMP", 0)  # Push the value back on top of the stack
        self.vm.write_pop("THAT", 0)  # Pop the value into the array element pointed by THAT

    def evaluateExpression(self):
        """Evaluates an expression by compiling its terms and applying operators."""
        self.analyzeElement()  # Compile the first term in the expression
        # Continue to process operators and subsequent terms as long as the current token is an operator
        while self.isCurrentTokenAnOperator():
            operator = self.getCurrentOperator()
            self.moveToNextToken()  # Move past the operator to the next term
            self.analyzeElement()  # Compile the next term in the expression
            self.applyOperator(operator)  # Apply the operator between the terms

    def isCurrentTokenAnOperator(self) -> bool:
        """Checks if the current token is an operator."""
        operators = {'+', '-', '*', '/', '&', '|', '<', '>', '='}
        return self.tokenizer.tokens[self.tokenizer.token_counter] in operators

    def getCurrentOperator(self) -> str:
        """Retrieves the current operator token."""
        return self.tokenizer.tokens[self.tokenizer.token_counter]

    def applyOperator(self, operator: str):
        """Applies the operator to the terms previously and currently compiled."""
        operatorMapping = {
            '+': lambda: self.vm.write_arithmetic("ADD"),
            '-': lambda: self.vm.write_arithmetic("SUB"),
            '*': lambda: self.vm.write_call("Math.multiply", 2),
            '/': lambda: self.vm.write_call("Math.divide", 2),
            '&': lambda: self.vm.write_arithmetic("AND"),
            '|': lambda: self.vm.write_arithmetic("OR"),
            '<': lambda: self.vm.write_arithmetic("LT"),
            '>': lambda: self.vm.write_arithmetic("GT"),
            '=': lambda: self.vm.write_arithmetic("EQ"),
        }
        # Execute the corresponding VM writer command for the operator
        if operator in operatorMapping:
            operatorMapping[operator]()

    def analyzeElement(self):
        """Evaluates an element within the code."""
        if self.tokenizer.token_type() == "INT_CONST":
            self.vm.write_push("CONST", int(self.currentToken()))
            self.moveToNextToken()
            return

        elif self.tokenizer.token_type() == "STRING_CONST":
            self.processStringConstant(self.tokenizer.string_val())
            # self.moveToNextToken()
            return

        elif self.currentToken() in {"-", "~", "^", "#"}:
            symbol = self.currentToken()
            self.moveToNextToken()
            # TODO: get rid of recursion
            self.analyzeElement()
            self.applySymbolOperation(symbol)
            return

        elif self.currentToken() == "(":

            self.moveToNextToken()
            self.evaluateExpression()
            self.moveToNextToken()
            return

        elif self.currentToken() in {"true", "false", "null", "this"}:
            self.handleConstant(self.currentToken())
            self.moveToNextToken()
            return


        elif self.tokenizer.token_type() == "IDENTIFIER" and self.getNextToken() != "(":
            identifier = self.currentToken()
            if self.getNextToken() not in ["[", "."]:
                self.manageVariableOrCall(identifier)
                self.moveToNextToken()
                return
            elif self.getNextToken() == "[":
                self.handleArrayAccess(identifier)
                return
        self.executeSubroutineInvocation()


    def processStringConstant(self, stringValue):
        """Handles the creation and population of a string constant."""
        self.vm.write_push("CONST", len(stringValue))  # Push the length of the string to the stack.
        self.vm.write_call("String.new", 1)  # Call the String.new function to create a new string object.
        for character in stringValue:
            self.vm.write_push("CONST", ord(character))  # Push the ASCII value of each character to the stack.
            self.vm.write_call("String.appendChar", 2)  # Call String.appendChar to append the character.
        self.moveToNextToken()  # Move past the string constant.

    def handleConstant(self, value: str):
        """Manages constant values."""
        actions = {
            "true": lambda: (self.vm.write_push("CONST", 0), self.vm.write_arithmetic("NOT")),
            "false": lambda: self.vm.write_push("CONST", 0),
            "null": lambda: self.vm.write_push("CONST", 0),
            "this": lambda: self.vm.write_push("POINTER", 0),
        }
        if value in actions:
            actions[value]()

    def applySymbolOperation(self, symbol: str):
        """Applies operations based on symbols."""
        operationMap = {
            "^": "SHIFTLEFT",
            "#": "SHIFTRIGHT",
            "-": "NEG",
            "~": "NOT"
        }
        if symbol in operationMap:
            self.vm.write_arithmetic(operationMap[symbol])

    def executeSubroutineInvocation(self):
        subroutineName = self.tokenizer.identifier()  # Extract the subroutine name
        self.moveToNextToken()  # Move to the next token to check for '(' or '.'

        if self.currentToken() == "(":
            # Method called from the same class, implicitly on 'this'
            self.vm.write_push("POINTER", 0)  # Push 'this' pointer
            self.moveToNextToken()  # Move past '('
            argumentCount = self.analyzeExpressionList() + 1  # +1 for 'this'
            self.moveToNextToken()
            self.vm.write_call(f"{self.className}.{subroutineName}", argumentCount)
        else:
            # External method call or a function call
            isMethodCall = False
            if self.symbols.type_of(subroutineName) != "NONE":
                # If it's a method of an object, push the object pointer
                self.vm.write_push(self.symbols.kind_of(subroutineName),
                                   self.symbols.index_of(subroutineName))
                isMethodCall = True

            self.moveToNextToken()  # Move past '.' to get the subroutine or class name
            nextSubroutineName = self.tokenizer.identifier()
            self.moveToNextToken()  # Move past the identifier to arguments list
            self.moveToNextToken()
            # TODO : might not work
            argumentCount = self.analyzeExpressionList() + (1 if isMethodCall else 0) # Adjust argument count for method call
            self.moveToNextToken()

            if isMethodCall:
                # Call method on the object
                objectType = self.symbols.type_of(subroutineName)
                self.vm.write_call(f"{objectType}.{nextSubroutineName}", argumentCount)
            else:
                # Call a function or constructor
                self.vm.write_call(f"{subroutineName}.{nextSubroutineName}", argumentCount)

    def analyzeExpressionList(self) -> int:
        """Analyzes a comma-separated list of expressions, returning the count."""
        argumentCount = 0
        if not self.currentToken() == ")":
            self.evaluateExpression()
            argumentCount += 1
            while self.currentToken() == ",":
                self.moveToNextToken()  # Skip the comma
                self.evaluateExpression()
                argumentCount += 1

        # self.moveToNextToken()  # Move past the closing ')' or to the next part of the subroutine call
        return argumentCount

    def countExpressions(self) -> int:
        """Counts the number of expressions."""
        expressions = 0
        if not self.stream.reachedEnd():
            self.buildExpression()
            expressions += 1
            while self.stream.currentValue() == ",":
                self.advance()
                self.buildExpression()
                expressions += 1
        return expressions

    def determineIdentifierAction(self):
        """Determines the action for an identifier."""
        if self.getNextToken() not in ["[", "."]:
            identifier = self.currentToken()
            self.manageVariableOrCall(identifier)
            self.moveToNextToken()
        elif self.getNextToken() == "[":
            self.handleArrayAccess(identifier)

    def manageVariableOrCall(self, identifier):
        """Manages variable usage or method calls."""
        kind = self.symbols.kind_of(identifier)
        index = self.symbols.index_of(identifier)
        self.vm.write_push(kind, index)

    def handleArrayAccess(self, identifier):
        """Handles array access."""
        kind = self.symbols.kind_of(identifier)
        index = self.symbols.index_of(identifier)

        self.vm.write_push(kind, index)
        self.moveToNextToken()
        self.moveToNextToken()

        self.evaluateExpression()
        self.vm.write_arithmetic("ADD")
        self.vm.write_pop("POINTER", 1)
        self.vm.write_push("THAT", 0)
        self.moveToNextToken()

