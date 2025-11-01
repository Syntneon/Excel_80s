import re

class FormulaFunctions:

    """
    Класс, содержащий реализацию функций Excel (СУММ, АБС, ЕСЛИ, СУММЕСЛИ).
    Он используется как "помощник" для FormulaEvaluator.
    """

    def __init__(self, sheet_instance):
       
        self.sheet = sheet_instance

    def _get_numeric_value(self, arg) -> int|float:
        """
        Универсальный метод для получения ЧИСЛЕННОГО значения из любого аргумента.
        Если аргумент - текст, который не конвертируется в число, возвращает 0.
        """
        if isinstance(arg, (int, float)):
            return arg
        if isinstance(arg, str) and re.match(r'^[A-Z]+\d+$', arg, re.IGNORECASE):
            value = self.sheet.get_cell_value(arg)
            if isinstance(value, str):
                return 0
            return value or 0
        try:
            return float(arg)
        except (ValueError, TypeError):
            return 0

    def SUM(self, *args) -> float:
        """
        Реализация функции СУММ.
        Принимает переменное количество аргументов, которые могут быть
        числами, ссылками на ячейки или уже раскрытыми диапазонами (в виде списков).
        """
        total = 0
        for arg in args:
            if isinstance(arg, list):
                total += sum(self._get_numeric_value(cell) for cell in arg)
            else:
                total += self._get_numeric_value(arg)
        return total

    def ABS(self, *args) -> float:
        """Реализация функции АБС.""" 
        if not args:                  
            return "#VALUE!"
        value = self._get_numeric_value(args[0])
        return abs(value)
   

    def IF(self, *args) -> float|str:
        """
        Реализация функции ЕСЛИ.
        Ожидает, что первый аргумент (условие) уже был вычислен
        парсером и пришел как True или False.
        """
        if len(args) != 3:
            return "#N/A"

        condition, true_val, false_val = args


        if condition:
            # Возвращаем значение, не обязательно числовое
            return self.sheet.get_cell_value(true_val) if isinstance(true_val, str) else true_val
        else:
            return self.sheet.get_cell_value(false_val) if isinstance(false_val, str) else false_val

    def expand_range(self, range_str: str) -> list:
        """
        Раскрывает диапазон 'A1:B2' в список ячеек ['A1', 'A2', 'B1', 'B2'].
        """
        try:
            start_cell, end_cell = range_str.split(':')
            
            start_col_str, start_row_str = self._split_cell_id(start_cell)
            end_col_str, end_row_str = self._split_cell_id(end_cell)

            start_col = ord(start_col_str.upper())
            end_col = ord(end_col_str.upper())
            start_row = int(start_row_str)
            end_row = int(end_row_str)

            cell_list = []
            for col in range(start_col, end_col + 1):
                for row in range(start_row, end_row + 1):
                    cell_list.append(f"{chr(col)}{row}")
            
            return cell_list
        except:
            # Если это не диапазон, возвращаем как есть
            return [range_str]

    def _split_cell_id(self, cell_id: str) -> tuple:
        """Разбивает 'A10' на ('A', '10')."""
        match = re.match(r"([A-Z]+)(\d+)", cell_id, re.IGNORECASE)
        if match:
            return match.groups()
        return None, None
   
