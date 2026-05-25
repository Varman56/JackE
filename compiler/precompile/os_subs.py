from compiler.precompile.subroutine_kind import SubroutineKind
from compiler.precompile.subroutine import Subroutine  # ваш класс Subroutine


class OsSubroutines:
    """Класс для инициализации функций операционной системы"""

    @staticmethod
    def get_table() -> dict[str, Subroutine]:
        table = {}

        # -------------------- Math --------------------
        # Все функции
        math_funcs = [
            ("multiply", SubroutineKind.function, 2, "int"),
            ("divide", SubroutineKind.function, 2, "int"),
            ("min", SubroutineKind.function, 2, "int"),
            ("max", SubroutineKind.function, 2, "int"),
            ("sqrt", SubroutineKind.function, 1, "int"),
            ("abs", SubroutineKind.function, 1, "int"),
            ("init", SubroutineKind.function, 0, "void"),
        ]
        for name, kind, n_args, ret_type in math_funcs:
            sub = Subroutine("Math", name, kind, n_args, ret_type)
            table[sub.get_full_name()] = sub

        # -------------------- String --------------------
        sub = Subroutine("String", "new", SubroutineKind.constructor, 1, "String")
        str_methods = [
            ("dispose", 0, "int"),
            ("length", 0, "int"),
            ("charAt", 1, "char"),
            ("setCharAt", 2, "void"),
            ("appendChar", 1, "String"),
            ("eraseLastChar", 0, "void"),
            ("intValue", 0, "int"),
            ("setInt", 1, "void"),
        ]
        str_funcs = [
            ("backSpace", 0, "char"),
            ("doubleQuote", 0, "char"),
            ("newLine", 0, "char"),
        ]

        table[sub.get_full_name()] = sub

        for name, n_args, ret_type in str_methods:
            sub = Subroutine("String", name, SubroutineKind.method, n_args, ret_type)
            table[sub.get_full_name()] = sub

        for name, n_args, ret_type in str_funcs:
            sub = Subroutine("String", name, SubroutineKind.function, n_args, ret_type)
            table[sub.get_full_name()] = sub

        # -------------------- Array --------------------
        sub = Subroutine("Array", "new", SubroutineKind.function, 1, "Array")
        table[sub.get_full_name()] = sub
        sub = Subroutine("Array", "dispose", SubroutineKind.method, 0, "void")
        table[sub.get_full_name()] = sub

        # -------------------- Output --------------------
        out_funcs = [
            ("moveCursor", 2, "void"),
            ("printChar", 1, "void"),
            ("printString", 1, "void"),
            ("printInt", 1, "void"),
            ("println", 0, "void"),
            ("backSpace", 0, "void"),
        ]
        for name, n_args, ret_type in out_funcs:
            sub = Subroutine("Output", name, SubroutineKind.function, n_args, ret_type)
            table[sub.get_full_name()] = sub

        # -------------------- Screen --------------------
        screen_funcs = [
            ("clearScreen", 0, "void"),
            ("setColor", 1, "void"),
            ("drawPixel", 2, "void"),
            ("drawLine", 4, "void"),
            ("drawRectangle", 4, "void"),
            ("drawCircle", 3, "void"),
        ]
        for name, n_args, ret_type in screen_funcs:
            sub = Subroutine("Screen", name, SubroutineKind.function, n_args, ret_type)
            table[sub.get_full_name()] = sub

        # -------------------- Keyboard --------------------
        kbd_funcs = [
            ("keyPressed", 0, "char"),
            ("readChar", 0, "char"),
            ("readLine", 1, "String"),
            ("readInt", 1, "int"),
        ]
        for name, n_args, ret_type in kbd_funcs:
            sub = Subroutine(
                "Keyboard", name, SubroutineKind.function, n_args, ret_type
            )
            table[sub.get_full_name()] = sub

        # -------------------- Memory --------------------
        mem_funcs = [
            ("peek", 1, "int"),
            ("poke", 2, "void"),
            ("alloc", 1, "Array"),
            ("deAlloc", 1, "void"),
        ]
        for name, n_args, ret_type in mem_funcs:
            sub = Subroutine("Memory", name, SubroutineKind.function, n_args, ret_type)
            table[sub.get_full_name()] = sub

        # -------------------- Sys --------------------
        sys_funcs = [
            ("halt", 0, "void"),
            ("error", 1, "void"),
            ("wait", 1, "void"),
            ("exit", 0, "void"),
        ]
        for name, n_args, ret_type in sys_funcs:
            sub = Subroutine("Sys", name, SubroutineKind.function, n_args, ret_type)
            table[sub.get_full_name()] = sub

        return table
