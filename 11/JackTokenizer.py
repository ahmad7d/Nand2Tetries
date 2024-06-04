import typing

class JackTokenizer:
    def __init__(self, input_stream: typing.TextIO) -> None:
        """Initializes the processor by reading and processing the input stream.

        Args:
            input_stream (typing.TextIO): The input stream containing code.
        """
        self.input_lines = input_stream.read().splitlines()
        self.processed_lines = self._process_input_lines(self.input_lines)
        self.true_false_map = self._mark_block_comment_lines(self.input_lines)
        self._clear_and_remove_marked_lines()
        self.token_counter = 0
        self.symbols = ['{', '}', '(', ')', '[', ']', '.', ',', ';', '+',
                        '-', '*', '/', '&', '|', '<', '>', '=', '~', '^', '#']
        self.symbols = set("{}()[].,;+-*/&|<>=~")
        self.keywords = set(["class", "constructor", "function", "method", "field", "static", "var", "int",
                             "char", "boolean", "void", "true", "false", "null", "this", "let", "do", "if",
                             "else", "while", "return"])
        self.tokens = []


        self._tokenize(self.processed_lines)




    def _strip_inline_comments(self, line: str) -> str:
        quote_index = line.find('"')
        comment_index = line.find("//")
        if comment_index != -1:
            if quote_index != -1 and quote_index < comment_index < line.find('"', quote_index + 1):
                return line
            return line[:comment_index]
        return line

    def _strip_block_comments(self, line: str) -> str:
        start_index = line.find("/*")
        end_index = line.find("*/", start_index + 2)
        if start_index != -1 and end_index != -1:
            if line.find('"') != -1 and line.find('"') < start_index:
                return line
            return line[:start_index] + line[end_index + 2:]
        return line

    def _normalize_whitespace(self, line: str) -> str:
        return line.replace("\t", " ").replace("\n", "").strip()

    def _process_input_lines(self, input_lines):
        processed_lines = []
        for line in input_lines:
            line = self._strip_inline_comments(line)
            line = self._strip_block_comments(line)
            line = self._normalize_whitespace(line)
            processed_lines.append(line)
        return processed_lines

    def _mark_block_comment_lines(self, input_lines):
        """Alternative implementation to mark lines within block comments.

        Args:
            input_lines (list[str]): Lines of code to process.

        Returns:
            list[bool]: Each element indicates if the corresponding line is within block comments.
        """
        in_block_comment = False
        true_false = []

        for line in input_lines:
            if "/*" in line and not in_block_comment:
                in_block_comment = True
                true_false.append(True)
                if "*/" in line:  # Handles case where start and end are on the same line
                    in_block_comment = False
            elif "*/" in line and in_block_comment:
                true_false.append(True)
                in_block_comment = False
            else:
                true_false.append(in_block_comment)
            # Handle the case where block comments start and end on the same line after being already inside a block comment
            if in_block_comment and "/*" in line and "*/" in line:
                index_of_end_comment = line.find("*/") + 2
                index_of_start_comment = line.find("/*")
                if index_of_end_comment < index_of_start_comment:
                    in_block_comment = True
                else:
                    in_block_comment = False

        return true_false

    def _clear_and_remove_marked_lines(self):
        """Clears lines marked as True in true_false_map and removes empty lines."""
        # Clearing lines within block comments
        for i, is_in_comment in enumerate(self.true_false_map):
            if is_in_comment:
                self.processed_lines[i] = ""

        # Removing empty lines
        self.processed_lines = [line for line in self.processed_lines if line]

    def _tokenize(self, lines):
        for line in lines:
            tokens = self._extract_tokens(line)
            self.refine_tokens(tokens)

    def _extract_tokens(self, line):
        if '"' not in line:
            return line.split()
        return self._split_with_strings(line)

    def _split_with_strings(self, line):
        tokens, temp, in_string = [], "", False
        for char in line:  # No need to convert string to list
            if char == '"' and not in_string:
                # If we encounter a string start and we're not already in a string
                if temp:  # Push any accumulated token before the string
                    tokens.extend(temp.split())
                    temp = ""
                in_string = True
                temp += char
            elif char == '"' and in_string:
                # If we encounter a string end and we're in a string
                temp += char
                tokens.append(temp)  # Append the whole string as a single token
                temp, in_string = "", False
            else:
                temp += char
        if temp:
            # Handle the last token after the loop
            if in_string:  # If it ends with an unterminated string
                tokens.append(temp)  # Add it as is, as a single token
            else:
                tokens.extend(temp.split())  # Otherwise, split normally
        return tokens

    def refine_tokens(self, lines):
        refined_tokens = []
        for line in lines:
            in_string = False
            current_token = ""
            for char in line:
                if char == '"' and not in_string:
                    # Beginning of string literal
                    in_string = True
                    if current_token:  # Push any token accumulated so far
                        refined_tokens.append(current_token)
                        current_token = char
                    else:
                        current_token += char
                elif char == '"' and in_string:
                    # End of string literal
                    current_token += char
                    refined_tokens.append(current_token)
                    current_token = ""
                    in_string = False
                elif not in_string and char in self.symbols:
                    # Symbol outside of string literal
                    if current_token:  # Push the token before the symbol
                        refined_tokens.append(current_token)
                    refined_tokens.append(char)  # Push the symbol as a separate token
                    current_token = ""
                elif char == " " and not in_string:
                    # Space outside of string literal
                    if current_token:
                        refined_tokens.append(current_token)
                        current_token = ""
                else:
                    # Regular character or inside string literal
                    current_token += char
            if current_token:  # Push the last token if any
                refined_tokens.append(current_token)
        self.tokens.extend(refined_tokens)   # Assuming you want to store the refined tokens

    def has_more_tokens(self) -> bool:
        """Checks if there are more tokens available for processing."""
        return self.token_counter < len(self.tokens)

    def advance(self) -> None:
        """Gets the next token from the input and makes it the current token.
        This method should be called if has_more_tokens() is true.
        Initially there is no current token.
        """
        if self.has_more_tokens():
            self.token_counter += 1

    def token_type(self) -> str:
        """
        Identifies the category of the current token.

        Returns:
            str: Category of the current token, one of:
                 - "KEYWORD" for language keywords,
                 - "SYMBOL" for programming symbols,
                 - "INT_CONST" for integer constants,
                 - "STRING_CONST" for string constants,
                 - "IDENTIFIER" for variable names and identifiers.
        """
        token = self.tokens[self.token_counter]  # Access the recently advanced token
        if token in self.keywords:
            return "KEYWORD"
        elif token in self.symbols:
            return "SYMBOL"
        elif token.isdigit():
            return "INT_CONST"
        elif token.startswith('"') and token.endswith('"'):
            return "STRING_CONST"
        else:
            return "IDENTIFIER"

    def keyword(self) -> str:
        """
        Retrieves the keyword of the current token, assuming it's a keyword.

        Returns:
            str: The current token as an uppercase keyword if it's a keyword type.
                 Expected keywords include programming and control structure keywords
                 such as "CLASS", "METHOD", "FUNCTION", "CONSTRUCTOR", "INT", "BOOLEAN",
                 "CHAR", "VOID", "VAR", "STATIC", "FIELD", "LET", "DO", "IF", "ELSE",
                 "WHILE", "RETURN", "TRUE", "FALSE", "NULL", "THIS".
        """
        return self.tokens[self.token_counter].upper()  # Considering the recent advancement

    def symbol(self) -> str:
        """
        Retrieves the symbol of the current token, assuming it's a symbol.

        Returns:
            str: The current token if it's a symbol. Expected symbols include
                 braces, parentheses, operators, and other special characters like
                 '{', '}', '(', ')', '[', ']', '.', ',', ';', '+', '-', '*', '/',
                 '&', '|', '<', '>', '=', '~', '^', '#'.
        """
        for symbol in self.symbols:
            if symbol in self.tokens[self.token_counter]:
                return symbol

    def identifier(self) -> str:
        """
        Returns:
            str: the identifier which is the current token.
            Should be called only when token_type() is "IDENTIFIER".
            Recall that identifiers were defined in the grammar like so:
            identifier: A sequence of letters, digits, and underscore ('_') not
                  starting with a digit. You can assume keywords cannot be
                  identifiers, so 'self' cannot be an identifier, etc'.
        """
        if self.token_type() == "IDENTIFIER":
            return self.tokens[self.token_counter]

    def int_val(self) -> int:
        """
        Returns:
            str: the integer value of the current token.
            Should be called only when token_type() is "INT_CONST".
            Recall that integerConstant was defined in the grammar like so:
            integerConstant: A decimal number in the range 0-32767.
        """
        intVal = int(self.tokens[self.token_counter])
        return intVal

    def string_val(self) -> str:
        """
        Returns:
            str: the string value of the current token, without the double
            quotes. Should be called only when token_type() is "STRING_CONST".
            Recall that StringConstant was defined in the grammar like so:
            StringConstant: '"' A sequence of Unicode characters not including
                      double quote or newline '"'
        """
        strVal = self.tokens[self.token_counter][1:-1]
        return strVal


    def current_token(self):
        return self.tokens[self.token_counter]