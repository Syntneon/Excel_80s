import re
from functions import FormulaFunctions

class FormulaEvaluator:
    def __init__(self, sheet_instance):
        """
        Конструктор принимает экземпляр Sheet, чтобы иметь доступ
        к значениям других ячеек.
        """
        self.sheet = sheet_instance   
        self.cache = {} # Кэш для хранения уже вычисленных значений ячеек в рамках одной сессии
        self.functions = None
        self.eval_globals = None

    def _initialize_helpers(self):
        """
        Метод "ленивой" инициализации.
        Создает все необходимые объекты-помощники, но только один раз.
        """
        if self.functions is None:
            self.functions = FormulaFunctions(self.sheet)
            self.eval_globals = {
                'СУММ': self.functions.SUM,
                'АБС': self.functions.ABS,
                'ЕСЛИ': self.functions.IF,
                #'СУММЕСЛИ': self.functions.SUMIF,
                #'abs': abs,
                #'sum': sum,
            }
        
    def _evaluate_simple_expression(self, formula_str: str):
        try:
            cell_references = re.findall(r'[A-Z]+\d+', formula_str, re.IGNORECASE)
            for ref_id in cell_references:
                ref_value = self.sheet.get_cell_value(ref_id)
                if ref_value is None or ref_value == '':
                    ref_value = 0
                formula_str = formula_str.replace(ref_id, str(ref_value))
                
            return eval(formula_str)
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
        Вычисляет формулы СУММ, АБС, ЕСЛИ СУММЕСЛИ.
        """
        try:
            # 1. Заменяем диапазоны на списки
            range_matches = re.findall(r'([A-Z]+\d+:[A-Z]+\d+)', formula_str, re.IGNORECASE)
            for range_str in range_matches:
                expanded_list = self.functions.expand_range(range_str)
                formula_str = formula_str.replace(range_str, str(expanded_list))

            # 2. Собираем локальные переменные (значения ячеек)
            eval_locals = {}
            cell_references = re.findall(r'[A-Z]+\d+', formula_str, re.IGNORECASE)
            for ref_id in cell_references:
                eval_locals[ref_id] = self.sheet.get_cell_value(ref_id) or 0
            
            # 3. Адаптируем синтаксис для Python (заменяем ';' на ',')
            formula_str = formula_str.replace(';', ',')
            
            # 4. Выполняем eval с доступом к нашим глобальным функциям
            result = eval(formula_str, self.eval_globals, eval_locals)
            return result
        except Exception as e:
            return f"#ERROR!({e})"


    def evaluate(self, cell_id: str, formula_str: str) -> int|float:
        """
        Главная точка входа. Сначала инициализирует помощников (если нужно),
        а затем выбирает стратегию вычисления.
        """
        # Возвращаем значение из кэша, если оно есть
        if cell_id in self.cache:
            return self.cache[cell_id]

        # 1. Вызываем ленивую инициализацию.
        self._initialize_helpers()

        # 2. Анализируем формулу и выбираем нужный вычислитель.
        pattern = r'\b(СУММ|АБС|ЕСЛИ|СУММЕСЛИ)\b'
        if re.search(pattern, formula_str, re.IGNORECASE):
            result = self._evaluate_with_functions(formula_str)
        else:
            result = self._evaluate_simple_expression(formula_str)
        
        # 3. Сохраняем результат в кэш и возвращаем его
        self.cache[cell_id] = result
        return result


  