#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess
import sys
import os

def main():
    """
    Покроково викликає інші файли:
      1) generate_persons.py
      2) generate_prompts.py
      3) refine_prompts.py
      4) generate_dialogues.py

    Припускаємо, що всі ці файли лежать в тій самій директорії,
    і кожен має свій 'if __name__ == "__main__":' блок.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))

    scripts = [
        "generate_persons.py",
        "generate_prompts.py",
        "refine_prompts.py",
        "generate_dialogues.py"
    ]

    for script in scripts:
        script_path = os.path.join(script_dir, script)
        if not os.path.exists(script_path):
            print(f"❌ Не знайдено файл {script}")
            return
        print(f"\n=== Запуск {script} ===")
        ret = subprocess.run([sys.executable, script_path])
        if ret.returncode != 0:
            print(f"❌ Помилка під час виконання {script}. Код {ret.returncode}")
            return
        print(f"✅ {script} виконано успішно.\n")

    print("Усі кроки завершено!")

if __name__ == "__main__":
    main()