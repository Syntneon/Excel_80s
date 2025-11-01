from sheet import Sheet

def main():
    """
    Основная функция, которая запускает приложение.
    """
    file_path = "test_1.yml" # путь к файлу
    my_sheet = Sheet()

    try:
        # 3. Загружаем данные из файла
        my_sheet.load_from_file(file_path)
        print(f"Файл '{file_path}' успешно загружен.")
        
        # 4. Вычисляем все ячейки
        print("Вычисление формул...")
        my_sheet.compute_all()
        print("Вычисления завершены.")
        
        # 5. Отображаем финальную таблицу
        my_sheet.display()
        
    except FileNotFoundError:
        print(f"[bold red]Ошибка: Файл '{file_path}' не найден.[/bold red]")
    except Exception as e:
        print(f"[bold red]Произошла непредвиденная ошибка: {e}[/bold red]")


if __name__ == "__main__":
    main()

