import subprocess
import os
import json

contas = [
    {"nome": "Conta 1 - Roxingo",            "tid": "ak-6pDTu1xBPp1jPG08LXK1K8", "tsec": "as-f8CE8vvKRJdL8BODP1FSkj"},
    {"nome": "Conta 2 - Apollo",              "tid": "ak-CKDiZCpjvSID4kKFqHDTLW", "tsec": "as-BVr4kDdhZe0cfsN72G6afz"},
    {"nome": "Conta 3 - Descarga News",       "tid": "ak-R0l3SdA2jE4WhX4BMVY9ji", "tsec": "as-NwJ7LOI9N3K7Fy982sMKEm"},
    {"nome": "Conta 4 - Historias de 7 Dias", "tid": "ak-AXtOSYJJ0RTN3bItvgrma9", "tsec": "as-8E1C4r7BsOE07iYcvXmOlx"},
    {"nome": "Conta 5 - Macaco Driver",       "tid": "ak-MUU4bUBLOAANEwu1cvy0tu", "tsec": "as-rPvCfnaB00uAhuctXXS3sT"},
]

print("=" * 60)
print("VERIFICANDO SALDO DE TODAS AS CONTAS MODAL")
print("=" * 60)

for c in contas:
    env = os.environ.copy()
    env["MODAL_TOKEN_ID"] = c["tid"]
    env["MODAL_TOKEN_SECRET"] = c["tsec"]
    try:
        r = subprocess.run(
            ["modal", "billing", "report", "--for", "this month", "--json"],
            env=env,
            capture_output=True,
            text=True,
            timeout=30
        )
        if r.returncode == 0 and r.stdout.strip():
            data = json.loads(r.stdout)
            gasto = sum(float(item.get("cost", 0)) for item in data)
            saldo = max(0.0, 30.0 - gasto)
            status = "DISPONIVEL" if saldo > 1.0 else "ESGOTADA"
            print(f"[{status}] {c['nome']}")
            print(f"         Gasto: ${gasto:.2f} | Saldo: ${saldo:.2f}")
        else:
            err = r.stderr.strip()[:200]
            print(f"[ERRO] {c['nome']}")
            print(f"       {err}")
    except Exception as e:
        print(f"[EXCECAO] {c['nome']}: {e}")
    print()

print("=" * 60)
