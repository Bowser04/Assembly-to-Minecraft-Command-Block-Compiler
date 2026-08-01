"""
Symbol table and context tracking for label resolution.
"""

class SymbolTable:
    """Tracks labels and their associated instruction addresses (indices)."""

    def __init__(self):
        self.labels: dict[str, int] = {}

    def add_label(self, name: str, instruction_id: int) -> None:
        """Register a label with its zero-based instruction index."""
        if name in self.labels:
            raise ValueError(f"Duplicate label error: '{name}' is already defined.")
        self.labels[name] = instruction_id

    def get_label_id(self, name: str) -> int:
        """Retrieve the instruction index associated with a label."""
        if name not in self.labels:
            raise KeyError(f"Undefined label error: Jump target '{name}' does not exist.")
        return self.labels[name]

    def has_label(self, name: str) -> bool:
        """Check if a label exists in the symbol table."""
        return name in self.labels
