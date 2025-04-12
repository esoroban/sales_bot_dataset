#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess
import sys
import os

GLOBAL_EXAMPLES_LIMIT = 5
RUN_REFINE_DIALOGUES = False  # Переключатель для улучшателя диалогов

def main():
    """
    Запускает файлы:
      1) generate_persons.py
      2) generate_prompts.py
      3) refine_prompts.py
      4) generate_dialogues.py
      5) refine_dialogues.py (опционально)

    Каждый файл получает GLOBAL_EXAMPLES_LIMIT в качестве аргумента.
    При запуске файла напрямую используется локальная константа.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))

    scripts = [
        "generate_persons.py",
        "generate_prompts.py",
        "refine_prompts.py",
        "generate_dialogues.py"
    ]

    if RUN_REFINE_DIALOGUES:
        scripts.append("refine_dialogues.py")

    for script in scripts:
        script_path = os.path.join(script_dir, script)
        if not os.path.exists(script_path):
            print(f"❌ Не найден файл {script}")
            return
        print(f"\n=== Запуск {script} с ограничением {GLOBAL_EXAMPLES_LIMIT} ===")
        ret = subprocess.run([sys.executable, script_path, str(GLOBAL_EXAMPLES_LIMIT)])
        if ret.returncode != 0:
            print(f"❌ Ошибка выполнения {script}. Код {ret.returncode}")
            return
        print(f"✅ {script} выполнен успешно.\n")
    
    print("Все шаги завершены!")

if __name__ == "__main__":
    main()
