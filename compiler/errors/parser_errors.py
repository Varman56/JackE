class ErrorUnexpectedGoToState(SyntaxError):
    def __init__(self, state_before: int, rule_left: str) -> None:
        super().__init__(
            f"Unexpected state in goto table. Last state:{state_before}; Rule's left: {rule_left}"
        )


ERR_UNEXPECTED_STATE = SyntaxError("unexpected state in action table")
