import csv

from compiler.grammar.automata import Automata


class SLRParser:
    """Класс для построения таблицы slr анализатора

     Аргументы:
    - filename: Путь до файла грамматики
    - outfile: Путь  куда будет сохранена таблица slr анализатора"""

    def __init__(
        self, filename: str = "grammar.slr", outfile: str = "jack_slr_table.csv"
    ):
        self.automata = Automata(filename)
        self.reader = self.automata.reader
        self.action_table: dict[tuple[int, str], str] = {}
        self.goto_table: dict[tuple[int, str], int] = {}
        self.errors: list[str] = []
        self._build_tables()
        self._save_table_to_csv(outfile)

    def _build_tables(self) -> None:
        """Построение таблицы slr анализатора"""
        for i, state in enumerate(self.automata.states):
            for item in state:
                if item.next_symbol is None:
                    if item.rule.left == self.reader.rules[0].left:
                        self._set_action(i, "EOF", "ACC")
                    else:
                        follow_set = self.automata.follow.get(item.rule.left, set())
                        for terminal in follow_set:
                            self._set_action(i, terminal, f"R{item.rule.id}")

                else:
                    symbol = item.next_symbol
                    next_idx = self.automata.transitions.get((i, symbol))

                    if next_idx is not None:
                        if symbol in self.reader.terminals:
                            self._set_action(i, symbol, f"S{next_idx}")
                        else:
                            self.goto_table[(i, symbol)] = next_idx

    def _log_conflict(
        self, state_idx: int, terminal: str, existing_action: str, new_action: str
    ) -> str:
        """Формаирование информации о конфликте в таблицу"""
        state = self.automata.states[state_idx]
        lines = list()
        lines.append(
            f"=== Конфликт в состоянии {state_idx} по символу '{terminal}' ==="
        )
        lines.append(f"Действия: {existing_action} vs {new_action}")

        if existing_action.startswith("S") and new_action.startswith("R"):
            lines.append("Тип: shift/reduce (оставлен shift)")
        elif existing_action.startswith("R") and new_action.startswith("S"):
            lines.append("Тип: shift/reduce (оставлен shift)")
        else:
            lines.append("Тип: reduce/reduce")

        lines.append("\nСостояние содержит пункты:")
        for item in state:
            lhs = item.rule.left
            rhs = item.rule.right
            dot = item.dot_pos
            before = rhs[:dot]
            after = rhs[dot:]
            rule_str = f"{lhs} -> {' '.join(before)} • {' '.join(after)}"
            if item.next_symbol is None:
                lines.append(f"  [R] {rule_str}  (правило {item.rule.id})")
            elif item.next_symbol == terminal:
                lines.append(f"  [S] {rule_str}  (shift по '{terminal}')")
            else:
                lines.append(f"      {rule_str}")

        lines.append("\nFOLLOW-множества нетерминалов, участвующих в свёртках:")
        for item in state:
            if item.next_symbol is None:
                lhs = item.rule.left
                f_set = self.automata.follow.get(lhs, set())
                lines.append(f"  FOLLOW({lhs}) = {{ {', '.join(sorted(f_set))} }}")

        lines.append("=============================================\n")
        return "\n".join(lines)

    def _set_action(self, state_idx: int, terminal: str, action: str):
        """Сохранение действия по таблице"""
        current = self.action_table.get((state_idx, terminal))
        if current and current != action:
            conflict_msg = self._log_conflict(state_idx, terminal, current, action)
            self.errors.append(conflict_msg)
            if current.startswith("S") and action.startswith("R"):
                return
        self.action_table[(state_idx, terminal)] = action

    def _save_table_to_csv(self, filename):
        """Сохранить таблицу в csv"""
        terminals = sorted(list(self.reader.terminals))
        non_terminals = sorted(
            list(self.reader.non_terminals - {self.reader.rules[0].left})
        )

        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            header = ["State"] + terminals + non_terminals
            writer.writerow(header)

            for i in range(len(self.automata.states)):
                row = [i]
                for t in terminals:
                    row.append(self.action_table.get((i, t), ""))
                for nt in non_terminals:
                    row.append(self.goto_table.get((i, nt), ""))
                writer.writerow(row)
