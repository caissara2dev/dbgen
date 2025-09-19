"""
Gerador de compras (CSV e XLSX) referenciando clientes existentes.

Regras:
- Cada compra contém: CódigoCliente, DataCompra, Valor, CódigoFilial
- Todo CódigoCliente deve existir na base de clientes (CSV informado)
- Cada cliente deve ter pelo menos uma compra
- Um cliente pode ter várias compras
- Quantidade total de linhas é ajustável; se menor que qtde de clientes, será elevada
- Valor de compra dentro de um intervalo configurável (valor mínimo e máximo)
- Período de datas configurável (início e fim)

Uso:
    python scripts/gerar_compras.py [clientes.csv] [linhas] [saida.csv] [saida.xlsx]
    Opções:
      --valor-min 10.0 --valor-max 1000.0
      --inicio 2024-01-01 --fim 2024-12-31
      --filiais 5
      --seed 42
"""

from __future__ import annotations

import argparse
import csv
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Iterable, List

from openpyxl import Workbook


def carregar_codigos_clientes(caminho_csv: str) -> list[str]:
    """Lê o CSV de clientes e retorna a lista de códigos de cliente.

    Aceita cabeçalho 'CódigoCliente' (preferencial) ou 'CodigoCliente'.
    """
    codigos: list[str] = []
    with open(caminho_csv, newline='', encoding='utf-8') as f:
        r = csv.DictReader(f)
        # Detecta nome de coluna compatível
        field = None
        for cand in ('CódigoCliente', 'CodigoCliente', 'Codigo', 'Código'):
            if cand in (r.fieldnames or []):
                field = cand
                break
        if not field:
            raise ValueError("Não encontrei a coluna de código do cliente no CSV (esperado: 'CódigoCliente').")
        for row in r:
            codigo = (row.get(field) or '').strip()
            if codigo:
                codigos.append(codigo)
    if not codigos:
        raise ValueError("Nenhum código de cliente encontrado no arquivo informado.")
    return codigos


def gerar_datas(n: int, inicio: datetime, fim: datetime, rng: random.Random) -> list[str]:
    """Gera n datas aleatórias no formato YYYY-MM-DD entre [inicio, fim]."""
    if fim < inicio:
        raise ValueError('Data fim é anterior à data início.')
    delta = (fim - inicio).days
    if delta < 0:
        delta = 0
    datas = []
    for _ in range(n):
        offset = rng.randint(0, delta) if delta > 0 else 0
        d = inicio + timedelta(days=offset)
        datas.append(d.strftime('%Y-%m-%d'))
    return datas


def gerar_filiais(qtd: int) -> list[str]:
    """Gera códigos de filial no formato F001, F002, ..."""
    qtd = max(1, int(qtd))
    return [f'F{i:03d}' for i in range(1, qtd + 1)]


def escolher(iterable: Iterable[str], rng: random.Random) -> str:
    return rng.choice(list(iterable))


def montar_compras(
    codigos_clientes: list[str],
    total_linhas: int,
    valor_min: float,
    valor_max: float,
    datas: list[str],
    filiais: list[str],
    rng: random.Random,
) -> list[tuple[str, str, float, str]]:
    """Monta a lista de compras garantindo ao menos 1 por cliente.

    Retorna tuplas (codigo_cliente, data_iso, valor_float, codigo_filial).
    """
    if valor_max < valor_min:
        raise ValueError('valor_max deve ser >= valor_min')

    # Garante ao menos 1 por cliente
    total_linhas = max(total_linhas, len(codigos_clientes))

    rows: list[tuple[str, str, float, str]] = []

    # Pré-semeia uma compra para cada cliente
    for idx, cod in enumerate(codigos_clientes):
        data = datas[idx % len(datas)]
        valor = round(rng.uniform(valor_min, valor_max), 2)
        filial = escolher(filiais, rng)
        rows.append((cod, data, valor, filial))

    # Distribui o restante
    faltantes = total_linhas - len(rows)
    for i in range(faltantes):
        cod = escolher(codigos_clientes, rng)
        data = datas[(len(rows) + i) % len(datas)]
        valor = round(rng.uniform(valor_min, valor_max), 2)
        filial = escolher(filiais, rng)
        rows.append((cod, data, valor, filial))

    return rows


def escrever_csv(caminho: str, header: list[str], rows: list[tuple[str, str, float, str]]) -> None:
    with open(caminho, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(header)
        for cod, data, valor, filial in rows:
            # CSV mantém ponto decimal; Excel/locale podem exibir com vírgula
            w.writerow([cod, data, f"{valor:.2f}", filial])


def escrever_xlsx(caminho: str, aba: str, header: list[str], rows: list[tuple[str, str, float, str]]) -> None:
    wb = Workbook()
    ws = wb.active
    ws.title = aba
    ws.append(header)
    # Escreve linhas garantindo que 'Valor' seja numérico e formatado
    for idx, (cod, data, valor, filial) in enumerate(rows, start=2):
        ws.append([cod, data, valor, filial])
        c = ws.cell(row=idx, column=3)
        # Formato de moeda; Excel exibira separadores conforme locale (pt-BR -> 1.234,56)
        c.number_format = 'R$ #,##0.00'
        # Para alterar, edite a string acima (ex.: '#,##0.00' ou 'R$ #,##0.00;-R$ #,##0.00')
    wb.save(caminho)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description='Gerar base de compras referenciando clientes existentes.')
    p.add_argument('clientes_csv', nargs='?', default='clientes_ficticios.csv', help='Caminho para o CSV de clientes (padrão: clientes_ficticios.csv)')
    p.add_argument('linhas', nargs='?', type=int, default=5000, help='Qtde total de linhas de compras (padrão: 5000)')
    p.add_argument('saida_csv', nargs='?', default='compras.csv', help='Arquivo CSV de saída (padrão: compras.csv)')
    p.add_argument('saida_xlsx', nargs='?', default=None, help='Arquivo XLSX de saída (padrão: mesmo nome do CSV)')
    p.add_argument('--valor-min', dest='valor_min', type=float, default=50.0, help='Valor mínimo por compra (padrão: 50.0)')
    p.add_argument('--valor-max', dest='valor_max', type=float, default=2000.0, help='Valor máximo por compra (padrão: 2000.0)')
    p.add_argument('--inicio', default='2024-01-01', help='Data inicial no formato YYYY-MM-DD (padrão: 2024-01-01)')
    p.add_argument('--fim', default='2024-12-31', help='Data final no formato YYYY-MM-DD (padrão: 2024-12-31)')
    p.add_argument('--filiais', type=int, default=5, help='Quantidade de filiais (padrão: 5)')
    p.add_argument('--seed', type=int, default=42, help='Seed para reprodutibilidade (padrão: 42)')
    return p.parse_args()


def main() -> None:
    args = parse_args()

    rng = random.Random(args.seed)

    clientes_csv = args.clientes_csv
    linhas = int(args.linhas)
    saida_csv = args.saida_csv
    saida_xlsx = args.saida_xlsx or str(Path(saida_csv).with_suffix('.xlsx'))

    # Carrega códigos de clientes
    codigos_clientes = carregar_codigos_clientes(clientes_csv)

    # Prepara datas e filiais
    inicio = datetime.strptime(args.inicio, '%Y-%m-%d')
    fim = datetime.strptime(args.fim, '%Y-%m-%d')
    datas = gerar_datas(max(linhas, len(codigos_clientes)), inicio, fim, rng)
    filiais = gerar_filiais(args.filiais)

    # Monta linhas de compras
    rows = montar_compras(
        codigos_clientes=codigos_clientes,
        total_linhas=linhas,
        valor_min=args.valor_min,
        valor_max=args.valor_max,
        datas=datas,
        filiais=filiais,
        rng=rng,
    )

    header = ['CódigoCliente', 'DataCompra', 'Valor', 'CódigoFilial']

    # Exporta CSV e XLSX
    escrever_csv(saida_csv, header, rows)
    escrever_xlsx(saida_xlsx, 'Compras', header, rows)


if __name__ == '__main__':
    main()
