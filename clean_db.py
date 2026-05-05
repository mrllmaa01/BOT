import sqlite3
from pathlib import Path

# Путь к базе данных
DB_PATH = Path(__file__).parent / "bot_database.db"

def clean_all_data():
    """Очищает все данные из таблиц, но сохраняет сами таблицы"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Получаем список всех таблиц
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    print("📊 Найденные таблицы:")
    for table in tables:
        table_name = table[0]
        if table_name != "sqlite_sequence":  # не трогаем служебную таблицу
            try:
                cursor.execute(f"DELETE FROM {table_name}")
                print(f"  ✅ Очищена таблица: {table_name}")
            except Exception as e:
                print(f"  ❌ Ошибка при очистке {table_name}: {e}")
    
    # Сбрасываем счетчики автоинкремента
    cursor.execute("DELETE FROM sqlite_sequence")
    
    conn.commit()
    conn.close()
    print("\n✅ Все данные успешно удалены!")
    print("   Структура базы данных сохранена.")

def drop_all_tables():
    """Удаляет все таблицы полностью (более радикально)"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Получаем список всех таблиц
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    print("📊 Удаление таблиц:")
    for table in tables:
        table_name = table[0]
        if table_name != "sqlite_sequence":
            try:
                cursor.execute(f"DROP TABLE {table_name}")
                print(f"  ✅ Удалена таблица: {table_name}")
            except Exception as e:
                print(f"  ❌ Ошибка при удалении {table_name}: {e}")
    
    conn.commit()
    conn.close()
    print("\n✅ Все таблицы удалены!")
    print("   База данных теперь пуста.")

if __name__ == "__main__":
    print("=" * 50)
    print("🧹 ОЧИСТКА БАЗЫ ДАННЫХ")
    print("=" * 50)
    print("\nВыбери действие:")
    print("1️⃣  Очистить данные (таблицы останутся)")
    print("2️⃣  Удалить все таблицы полностью")
    print("3️⃣  Выход")
    
    choice = input("\nТвой выбор (1/2/3): ").strip()
    
    if choice == "1":
        print("\n🔄 Очищаю данные...")
        clean_all_data()
    elif choice == "2":
        confirm = input("\n⚠️  ТОЧНО удалить все таблицы? (да/нет): ").strip().lower()
        if confirm == "да":
            print("\n🔄 Удаляю таблицы...")
            drop_all_tables()
        else:
            print("❌ Отменено")
    else:
        print("👋 Выход")