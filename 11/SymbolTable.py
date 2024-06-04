class SymbolTable:
    """
    Manages a two-level scope symbol table for a Jack compiler. It supports
    class-level and subroutine-level scopes with unique identifiers.
    """

    def __init__(self) -> None:
        """Initializes a new, empty symbol table."""
        self.global_scope = {}
        self.local_scope = {}
        self.counters = {"STATIC": 0, "FIELD": 0, "ARG": 0, "VAR": 0}

    def start_subroutine(self) -> None:
        """Resets the subroutine's symbol table, starting a new scope."""
        self.local_scope.clear()
        self.counters["ARG"], self.counters["VAR"] = 0, 0

    def define(self, symbol_name: str, symbol_type: str, kind: str) -> None:
        """Adds a new symbol to the appropriate scope with a unique index."""
        target_scope = self.local_scope if kind in ["ARG", "VAR"] else self.global_scope
        adjusted_kind = "THIS" if kind == "FIELD" else "LOCAL" if kind == "VAR" else kind
        index = self.counters[kind]
        target_scope[symbol_name] = (symbol_type, adjusted_kind, index)
        self.counters[kind] += 1

    def var_count(self, kind: str) -> int:
        """Returns the count of variables of the given kind in the current scope."""
        return self.counters[kind]

    def kind_of(self, identifier: str) -> str:
        """Determines the kind of the given identifier in the current scope."""
        if identifier in self.local_scope:
            return self.local_scope[identifier][1]
        if identifier in self.global_scope:
            return self.global_scope[identifier][1]
        return "NONE"

    def type_of(self, identifier: str) -> str:
        """Gets the type of the given identifier if it exists in any scope."""
        for scope in (self.local_scope, self.global_scope):
            if identifier in scope:
                return scope[identifier][0]
        return "NONE"

    def index_of(self, identifier: str) -> int:
        """Retrieves the index of the given identifier within its scope."""
        for scope in (self.local_scope, self.global_scope):
            if identifier in scope:
                return scope[identifier][2]
        return -1
