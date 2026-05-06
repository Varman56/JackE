from compiler.source.grammar.grammar_reader import GrammarReader
from compiler.source.grammar.item import Item


class Automata:
    def __init__(self, filename):
        self.reader = GrammarReader(filename)

        self.first = {}
        for t in self.reader.terminals:
            self.first[t] = {t}
        for nt in self.reader.non_terminals:
            self.first[nt] = set()
        self.follow = {nt: set() for nt in self.reader.non_terminals}
        self.start_symbol = self.reader.rules[0].left

        self.build_first()
        self.build_follow()

        self.states = []
        self.transitions = {}
        self.build_lr0_states()

    def build_first(self):
        changed = True
        while changed:
            changed = False
            for rule in self.reader.rules:
                if not rule.right:
                    continue

                lhs = rule.left
                first_symbol = rule.right[0]
                before_count = len(self.first[lhs])
                self.first[lhs].update(self.first[first_symbol])

                if len(self.first[lhs]) > before_count:
                    changed = True

    def build_follow(self):
        self.follow[self.start_symbol].add('$')

        changed = True
        while changed:
            changed = False
            for rule in self.reader.rules:
                lhs = rule.left
                rhs = rule.right

                for i in range(len(rhs)):
                    symbol = rhs[i]

                    if symbol in self.reader.non_terminals:
                        before_count = len(self.follow[symbol])

                        if i + 1 < len(rhs):
                            next_symbol = rhs[i + 1]
                            if next_symbol in self.reader.terminals:
                                self.follow[symbol].add(next_symbol)
                            else:
                                self.follow[symbol].update(self.first[next_symbol])

                        if i + 1 == len(rhs):
                            self.follow[symbol].update(self.follow[lhs])

                        if len(self.follow[symbol]) > before_count:
                            changed = True

    def print_info(self):
        print("--- FIRST Sets ---")
        for nt, symbols in sorted(self.first.items()):
            print(f"FIRST({nt:20}) = {{ {', '.join(sorted(symbols))} }}")

        print("\n--- FOLLOW Sets ---")
        for nt, symbols in sorted(self.follow.items()):
            print(f"FOLLOW({nt:20}) = {{ {', '.join(sorted(symbols))} }}")

    @staticmethod
    def state_to_key(items):
        return "|".join(sorted([str(item) for item in items]))

    def closure(self, items):
        closure_set = set(items)
        added_symbols = set()

        changed = True
        while changed:
            changed = False
            current_items = list(closure_set)
            for item in current_items:
                symbol = item.next_symbol
                if symbol and symbol in self.reader.non_terminals:
                    if symbol not in added_symbols:
                        added_symbols.add(symbol)
                        for rule in self.reader.rules:
                            if rule.left == symbol:
                                closure_set.add(Item(rule, 0))
                                changed = True
        return list(closure_set)

    def goto(self, items, symbol):
        new_set = []
        for item in items:
            if item.next_symbol == symbol:
                new_set.append(Item(item.rule, item.dot_pos + 1))
        return self.closure(new_set)

    def build_lr0_states(self):
        start_rule = self.reader.rules[0]
        initial_state = self.closure([Item(start_rule, 0)])

        self.states = [initial_state]
        state_keys = {self.state_to_key(initial_state): 0}

        queue = [0]
        while queue:
            curr_idx = queue.pop(0)
            curr_state = self.states[curr_idx]

            symbols = set()
            for item in curr_state:
                if item.next_symbol:
                    symbols.add(item.next_symbol)

            for symbol in symbols:
                next_state = self.goto(curr_state, symbol)
                if not next_state:
                    continue

                key = self.state_to_key(next_state)
                if key not in state_keys:
                    new_idx = len(self.states)
                    self.states.append(next_state)
                    state_keys[key] = new_idx
                    queue.append(new_idx)
                    self.transitions[(curr_idx, symbol)] = new_idx
                else:
                    self.transitions[(curr_idx, symbol)] = state_keys[key]
