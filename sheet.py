from rich.table import Table
from rich.console import Console
from pathlib import Path
from data_loader import Sheetloader
from formula_evaluator import FormulaEvaluator

class Sheet:
    """
        Выполняет отрисовку таблицы с данными и рассчитанными значениями.
    """
    def __init__(self):
        self.raw_cells: dict = {}
        self.computed_cells: dict = {}
        self.evaluator = None  

    def load_from_file(self, file_path: str | Path) -> None:
        """Загружает данные из файла."""
        loader = Sheetloader(Path(file_path))
        self.raw_cells = loader.load()

    def get_cell_value(self, cell_id: str) -> int|float:
        if cell_id in self.computed_cells:
            return self.computed_cells[cell_id]
        raw_value = self.raw_cells.get(cell_id)
        if isinstance(raw_value, str) and raw_value.startswith('='):
            if self.evaluator is None:
                self.evaluator = FormulaEvaluator(self)                          # подключение метода для рассчета ячейки
            computed_value = self.evaluator.evaluate(cell_id, raw_value[1:])
            self.computed_cells[cell_id] = computed_value
            return computed_value
        self.computed_cells[cell_id] = raw_value
        return raw_value
    
    def compute_all(self):
        """Вычисляет значения для всех ячеек, чтобы заполнить computed_cells."""
        self.computed_cells.clear()
        if self.evaluator:
            self.evaluator.cache.clear()
            
        for cell_id in self.raw_cells:
            self.get_cell_value(cell_id)

    def display(self) -> None:
        """Отображает сырые данные из таблицы с помощью Rich."""
        console = Console()
        table = Table(title="Содержимое таблицы", show_header=True)

        if not self.raw_cells:
            console.print("[red]Таблица пуста.[/red]")
            return
        
        # Динамически определяем столбцы и строки
        all_ids = self.raw_cells.keys()
        cols = sorted(list(set([c for c in ''.join(all_ids) if c.isalpha()])))
        rows = sorted(list(set([int(c.lstrip(''.join(cols))) for c in all_ids if c.lstrip(''.join(cols)).isdigit()])))
        max_row = max(rows)
        rows = list(range(1,max_row+1))
       
        # Добавляем колонку для номеров строк
        table.add_column("")

        # Добавляем колонки в таблицу Rich
        for col in cols:
            table.add_column(col, justify="center")
        
        # Заполняем ячейки в таблице
        for row in rows:
            row_data = [str(row)]
            for col in cols:
                sell_key = f'{col}{row}'
                value = self.computed_cells.get(sell_key, '')
                row_data.append(str(value)) if value is not None else ''
            table.add_row(*row_data)
        console.print(table)
            


        