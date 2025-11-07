class ExpressionParser:
    """
    Парсер для арифметических выражений.
    """
    def parse(self, expression: str) -> float:
        """
        Публичный метод, который является точкой входа.
        Он просто передает управление первому, самому низкому уровню приоритета.
        """
        return self._parse_level_1_add_subtract(expression)

    def _parse_level_1_add_subtract(self, expression: str) -> float:
        """
        Уровень 1: Обработка сложения (+) и вычитания (-).
        Это операции с самым низким приоритетом.
        """
        
        balance = 0
        for i in range(len(expression) - 1, -1, -1):
            char = expression[i]
            if char == ')': balance += 1
            elif char == '(': balance -= 1
            
            if balance == 0:
                if char == '+':  
                    return self._parse_level_1_add_subtract(expression[:i]) + self._parse_level_2_multiply_divide(expression[i+1:])
                if char == '-':
                    if i > 0 and expression[i-1].lower() not in '+-*/(^e':
                         return self._parse_level_1_add_subtract(expression[:i]) - self._parse_level_2_multiply_divide(expression[i+1:])

        return self._parse_level_2_multiply_divide(expression)

    def _parse_level_2_multiply_divide(self, expression: str) -> float:
        """
        Уровень 2: Обработка умножения (*) и деления (/).
        """
        balance = 0
        for i in range(len(expression) - 1, -1, -1):
            char = expression[i]
            if char == ')': balance += 1
            elif char == '(': balance -= 1

            if balance == 0:
                if char == '*':
                    return self._parse_level_2_multiply_divide(expression[:i]) * self._parse_level_3_power(expression[i+1:])
                if char == '/':
                    divisor = self._parse_level_3_power(expression[i+1:])
                    if divisor == 0: raise ZeroDivisionError
                    return self._parse_level_2_multiply_divide(expression[:i]) / divisor
        
        return self._parse_level_3_power(expression)

    def _parse_level_3_power(self, expression: str) -> float:
        """
        Уровень 3: Обработка возведения в степень (^).
       
        """
        balance = 0
        for i, char in enumerate(expression):
            if char == '(': balance += 1
            elif char == ')': balance -= 1

            if balance == 0 and char == '^':
                return self._parse_level_3_power(expression[:i]) ** self._parse_atom(expression[i+1:])
        
        
        return self._parse_atom(expression)

    def _parse_atom(self, expression: str) -> float:
        """
        Базовый уровень: обработка чисел, скобок и унарного минуса.
        Это "атом", самая неделимая часть выражения.
        """
        expression = expression.strip()
        
        if expression.startswith('(') and expression.endswith(')'):
            return self.parse(expression[1:-1])
        
        if expression.startswith('-'):
            return -self._parse_atom(expression[1:])

        try:
            return float(expression)
        except ValueError:
            raise ValueError(f"Не удалось распознать '{expression}'")
