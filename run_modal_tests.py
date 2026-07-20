import subprocess
import sys

def main():
    print("Iniciando Modal Run...")
    env = dict(sys.modules['os'].environ)
    env['PYTHONIOENCODING'] = 'utf-8'
    env['PYTHONUTF8'] = '1'

    process = subprocess.Popen(
        ["modal", "run", "backend/cloud_tools/test_universal_multiref.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        encoding="utf-8",
        errors="replace",
        env=env
    )

    with open("modal_log.txt", "w", encoding="utf-8") as f:
        for line in process.stdout:
            f.write(line)
    
    process.wait()
    print(f"Modal finalizado com código {process.returncode}")

if __name__ == "__main__":
    main()
