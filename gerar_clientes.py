"""
Gerador de base de clientes fictícios (CSV e XLSX).

- Nomes realistas com Faker (pt_BR)
- CPF válido (validate-docbr)
- Celular padronizado: (DD) 9XXXX-XXXX
- E-mail coerente com o nome: primeiro.sobrenome@dominio
- Código do cliente: c00001, c00002, ...

Uso:
    python scripts/gerar_clientes.py [qtd] [saida.csv] [saida.xlsx]
Ex.:
    python scripts/gerar_clientes.py 500 clientes.csv clientes.xlsx
"""

from __future__ import annotations

import csv
import random
import sys
import unicodedata
from pathlib import Path

from faker import Faker
from validate_docbr import CPF as CPFValidator
from openpyxl import Workbook

# Subconjunto plausível de DDDs brasileiros (não exaustivo)
DDDS = [
    11, 12, 13, 14, 15, 16, 17, 18, 19,
    21, 22, 24, 27, 28,
    31, 32, 33, 34, 35, 37, 38,
    41, 42, 43, 44, 45, 46, 47, 48, 49,
    51, 53, 54, 55,
    61, 62, 63, 64, 65, 66, 67, 68, 69,
    71, 73, 74, 75, 77, 79,
    81, 82, 83, 84, 85, 86, 87, 88, 89,
    91, 92, 93, 94, 95, 96, 97, 98, 99,
]


def remove_accents(s: str) -> str:
    """Remove acentos (útil para criar e-mails estáveis)."""
    return "".join(
        c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn"
    )


def gerar_cpf() -> str:
    """Gera CPF válido com máscara usando validate-docbr."""
    return CPFValidator().generate(mask=True)


def gerar_nome(fake: Faker) -> str:
    """Gera nome completo realista (pt_BR) e remove títulos (Sr./Dra./etc.)."""
    nome = fake.name()
    for t in ["Sr.", "Sra.", "Sr", "Sra", "Dr.", "Dra.", "Dr", "Dra", "Prof.", "Prof"]:
        nome = nome.replace(t + " ", "").replace(t, "")
    return nome.strip()


def gerar_celular() -> str:
    """Gera celular no padrão (DD) 9XXXX-XXXX com DDD plausível."""
    ddd = random.choice(DDDS)
    primeira = random.randint(0, 9999)
    segunda = random.randint(0, 9999)
    return f"({ddd:02d}) 9{primeira:04d}-{segunda:04d}"


def gerar_email_local(nome: str) -> str:
    """Cria o local-part do e-mail a partir do nome (primeiro.sobrenome)."""
    base = remove_accents(nome.lower())
    # Remove preposições comuns do português
    for p in [" da ", " de ", " do ", " dos ", " das "]:
        base = base.replace(p, " ")
    partes = [p for p in base.split() if p not in {"da", "de", "do", "dos", "das"}]
    if not partes:
        return "cliente"
    local = f"{partes[0]}.{partes[-1]}" if len(partes) >= 2 else partes[0]
    # Sanitiza: mantém apenas letras, números, ponto e hífen
    permitido = set("abcdefghijklmnopqrstuvwxyz0123456789.-")
    local = "".join(ch for ch in local if ch in permitido).strip(".")
    return local or "cliente"


def gerar_codigo(i: int) -> str:
    """Gera código sequencial no formato c00001."""
    return f"C{i:05d}"


def main() -> None:
    # Parse simples de argumentos com valores padrão
    qtd = int(sys.argv[1]) if len(sys.argv) > 1 else 200
    saida_csv = sys.argv[2] if len(sys.argv) > 2 else "clientes_ficticios.csv"
    saida_xlsx = sys.argv[3] if len(sys.argv) > 3 else str(Path(saida_csv).with_suffix(".xlsx"))

    fake = Faker("pt_BR")

    # Conjuntos para garantir unicidade de CPF e e-mail dentro do arquivo
    usados_cpf: set[str] = set()
    usados_email: set[str] = set()

    header = ["CódigoCliente", "NomeCompleto", "Celular", "CPF", "Email"]
    rows: list[list[str]] = []

    # Geração de registros
    for i in range(1, qtd + 1):
        nome = gerar_nome(fake)

        cpf = gerar_cpf()
        while cpf in usados_cpf:
            cpf = gerar_cpf()
        usados_cpf.add(cpf)

        local = gerar_email_local(nome)
        dominio = "example.com"
        email = f"{local}@{dominio}"
        contador = 2
        while email in usados_email:
            email = f"{local}{contador}@{dominio}"
            contador += 1
        usados_email.add(email)

        celular = gerar_celular()
        codigo = gerar_codigo(i)
        rows.append([codigo, nome, celular, cpf, email])

    # Exporta CSV (UTF-8)
    with open(saida_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)

    # Exporta XLSX (aba "Clientes")
    wb = Workbook()
    ws = wb.active
    ws.title = "Clientes"
    ws.append(header)
    for r in rows:
        ws.append(r)
    wb.save(saida_xlsx)


if __name__ == "__main__":
    main()

