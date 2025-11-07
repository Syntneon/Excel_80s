import re
from functions import FormulaFunctions
from expression import ExpressionParser

class FormulaEvaluator:
    def __init__(self, sheet_instance):
        """
        Конструктор принимает экземпляр Sheet, чтобы иметь доступ
        к значениям других ячеек.
        """
        self.sheet = sheet_instance   
        self.cache = {}
        self.functions = None
        self.eval_globals = None
        self.parser = None

    def _initialize_helpers(self):
        """
        Создает все необходимые объекты-помощники, но только один раз.
        """
        if self.functions is None:
            self.functions = FormulaFunctions(self.sheet)
            self.eval_globals = {
                'СУММ': self.functions.SUM,
                'АБС': self.functions.ABS,
                'ЕСЛИ': self.functions.IF,
                'СУММЕСЛИ': self.functions.SUMIF
            }
        if self.parser is None:
            self.parser = ExpressionParser()
    
    def _evaluate_simple_expression(self, formula_str: str):
        """
        Вычисляет математические операции
        """
        try:
            cell_references = re.findall(r'[A-Z]+\d+', formula_str, re.IGNORECASE)
            unique_refs = set(cell_references)
            sorted_refs = sorted(list(unique_refs), key=len, reverse=True)
            for ref_id in sorted_refs:
                ref_value = self.sheet.get_cell_value(ref_id)
                if ref_value is None or ref_value == '':
                    ref_value = 0
                formula_str = formula_str.replace(ref_id, str(ref_value))
                
            return self.parser.parse(formula_str)
        except ZeroDivisionError:
            return "#DIV/0!"
        except NameError as e:
            return f"#NAME? ({e})"
        except TypeError:
            return "#VALUE!"
        except Exception as e:
            return f"#ERROR: {e}"

    def _evaluate_with_functions(self, formula_str: str):
        """
        Вычисление функций
        """ 
        known_functions = {
            'СУММ': self.functions.SUM, 'АБС': self.functions.ABS,
            'ЕСЛИ': self.functions.IF, 'СУММЕСЛИ': self.functions.SUMIF
        }
        inner_func_pattern = re.compile(r'\b([A-ZА-Я_]+)\s*\(([^()]*)\)', re.IGNORECASE)

        while True:
            match = inner_func_pattern.search(formula_str)
            if not match: break 
            full_match, func_name, args_str = match.group(0), match.group(1).upper(), match.group(2)   
            if func_name not in known_functions:
                return f"#NAME? ({func_name})"
            evaluated_args = []
            if args_str:
                for arg in self._split_args(args_str):
                    if (arg.startswith('"') and arg.endswith('"')) or (arg.startswith("'") and arg.endswith("'")):
                        evaluated_args.append(arg[1:-1]) 
                    elif ':' in arg and '"' not in arg and "'" not in arg:
                        evaluated_args.append(arg)
                    else:
                        
                        evaluated_args.append(self._evaluate_simple_expression(arg)) 
            result = known_functions[func_name](*evaluated_args) 
            formula_str = formula_str.replace(full_match, str(result), 1)

        return self._evaluate_simple_expression(formula_str)
    def _split_args(self, args_str: str) -> list[str]:
        """
        Разбирает строку с аргументами, разделяя их по ';',
        игнорирует ; внутри кавычек или вложенных функций.
        """
        args = []
        current_arg = ""
        in_quotes = False
        paren_balance = 0
        for char in args_str:
            if char == '"': in_quotes = not in_quotes
            elif char == '(': paren_balance += 1
            elif char == ')': paren_balance -= 1
            
            if char == ';' and not in_quotes and paren_balance == 0:
                args.append(current_arg.strip())
                current_arg = ""
            else:
                current_arg += char
        args.append(current_arg.strip())
        return args

    def evaluate(self, cell_id: str, formula_str: str):
        if cell_id in self.cache:
            return self.cache[cell_id]
        self._initialize_helpers()
        pattern = r'\b(СУММ|АБС|ЕСЛИ|СУММЕСЛИ)\b'
        formula_str = formula_str.lstrip('=')
        if re.search(pattern, formula_str, re.IGNORECASE):
            result = self._evaluate_with_functions(formula_str)
        else:
            result = self._evaluate_simple_expression(formula_str)
        self.cache[cell_id] = result
        return result


  
