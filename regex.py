from __future__ import annotations
from abc import ABC, abstractmethod


class State(ABC):

    @abstractmethod
    def __init__(self) -> None:
        pass

    @abstractmethod
    def check_self(self, char: str) -> bool:
        """
        function checks whether occured character is handled by current ctate
        """
        pass

    def check_next(self, next_char: str) -> State | Exception:
        for state in self.next_states:
            if state.check_self(next_char):
                return state
        raise NotImplementedError("rejected string")


class StartState(State):


    def __init__(self):
        self.next_states: list[State] = []
        super().__init__()

    def check_self(self, char):
        return super().check_self(char)


class TerminationState(State):
    def __init__(self):
        super().__init__()

    def check_self(self, char):
        return False


class DotState(State):
    """
    state for . character (any character accepted)
    """


    def __init__(self):
        self.next_states: list[State] = []
        super().__init__()

    def check_self(self, char: str):
        return True


class AsciiState(State):
    """
    state for alphabet letters or numbers
    """


    curr_sym = ""

    def __init__(self, symbol: str) -> None:
        self.symbol = symbol
        self.next_states: list[State] = []

    def check_self(self, curr_char: str) -> State | Exception:
        if curr_char == self.symbol:
            return True

        return False


class StarState(State):



    def __init__(self, checking_state: State):
        self.checking_state = checking_state
        self.next_states: list[State] = []
        self.next_states.append(self.checking_state)
        self.checking_state.next_states.append(self)

    def check_self(self, char):
        for state in self.next_states:
            if state.check_self(char):
                return True

        return False


class PlusState(State):

    def __init__(self, checking_state: State):
        self.checking_state = checking_state
        self.next_states: list[State] = []
        self.next_states.append(self.checking_state)
        self.checking_state.next_states.append(self)

    def check_self(self, char):
        for state in self.next_states:
            if state.check_self(char):
                return True

        return False

class RegexFSM:


    def __init__(self, regex_expr: str) -> None:
        self.curr_state: State = StartState()
        prev_state = self.curr_state
        tmp_next_state = self.curr_state
        self._grand_prev = self.curr_state

        for char in regex_expr:
            tmp_next_state = self.__init_next_state(char, prev_state, tmp_next_state)
            prev_state.next_states.append(tmp_next_state)
            self._grand_prev = prev_state
            prev_state = tmp_next_state

        tmp_next_state = TerminationState()
        prev_state.next_states.append(tmp_next_state)
        prev_state = tmp_next_state

    def __init_next_state(
        self, next_token: str, prev_state: State, tmp_next_state: State
    ) -> State:
        new_state = None

        match next_token:
            case next_token if next_token == ".":
                new_state = DotState()
            case next_token if next_token == "*":
                new_state = StarState(tmp_next_state)
                if tmp_next_state in self._grand_prev.next_states:
                    self._grand_prev.next_states.remove(tmp_next_state)
                    self._grand_prev.next_states.append(new_state)

            case next_token if next_token == "+":
                new_state = PlusState(tmp_next_state)

            case next_token if next_token.isascii():
                new_state = AsciiState(next_token)

            case _:
                raise AttributeError("Character is not supported")

        return new_state

    def check_string(self, string):
        curr = {self.curr_state}
        for char in string:
            next_states = set()
            for state in curr:
                for next_state in state.next_states:
                    if isinstance(next_state, (StarState, PlusState)):
                        for sub in next_state.next_states:
                            if sub.check_self(char):
                                next_states.add(sub)
                    elif next_state.check_self(char):
                        next_states.add(next_state)
            if not next_states:
                return False
            curr = next_states

        return any(
            any(isinstance(n, TerminationState) for n in s.next_states)
            for s in curr
        )


if __name__ == "__main__":
    regex_pattern = "a*4.+hi"

    regex_compiled = RegexFSM(regex_pattern)

    print(regex_compiled.check_string("aaaaaa4uhi"))  # True
    print(regex_compiled.check_string("4uhi"))  # True
    print(regex_compiled.check_string("meow"))  # False
