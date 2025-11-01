import json
import yaml
from pathlib import Path


class Sheetloader:

    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.сells_data: dict = None

    def load(self) -> dict:
        """
        Выполняет загрузку и валидацию данных из файла.

        - Проверяет существование файла и его расширение.
        - Читает и парсит YAML или JSON.
        - Валидирует базовую структуру (наличие ключа 'cells').
        - Сохраняет результат в self.cells_data и возвращает его.
        """

        if not self.file_path.exists():
            raise FileNotFoundError(f"Файл не найден: {self.file_path}")
        if self.file_path.suffix.lower() not in ['.yml', '.yaml', '.json']:
            raise ValueError(f'Неподдерживаемый формат файла {self.file_path.suffix}')
        
        content = self.file_path.read_text(encoding='utf-8')

        try:
            if self.file_path.suffix in ['.yml', 'yaml']:
                data_from_file = yaml.safe_load(content)
            else:
                data_from_file = json.loads(content)
        except(json.JSONDecodeError, yaml.YAMLError) as e:
            raise ValueError(f'Ошибка парсинга файла: {e}') from e
        
        if not isinstance(data_from_file, dict) or 'cells' not in data_from_file:
            raise ValueError('Файл должен быть в виде словаря и содержать ключЖ cells')
        
        self.cells_data = data_from_file['cells']
        return self.cells_data