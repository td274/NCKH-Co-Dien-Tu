"""
run.py
Script chay doc lap cho pipeline thi giac.
Chay: D:\Python312\python.exe run.py
"""

import os
import sys
import subprocess

RUN_DIR = os.path.dirname(os.path.abspath(__file__))


def run_script(name):
    path = os.path.join(RUN_DIR, name)
    print(f"\n>>> Chay {name}")
    result = subprocess.run(
        [sys.executable, path],
        cwd=RUN_DIR,
        text=True,
        encoding='utf-8'
    )
    if result.returncode != 0:
        print(f"[CANH BAO] {name} thoat voi ma {result.returncode}")
    return result.returncode == 0


def main():
    # Dam bao dataset duoc sinh
    run_script('generate_dataset.py')

    # Danh gia tren tap tong hop
    run_script('evaluate_only.py')

    # Thu webcam
    run_script('webcam_test.py')

    print("\n===== HOAN THANH =====")
    print("Ket qua chi tiet xem KETQUA.md, output/metrics.json va figures/")


if __name__ == '__main__':
    main()
