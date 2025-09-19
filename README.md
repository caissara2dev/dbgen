# Brazilian Client & Purchase Data Generators

Generate realistic, Brazil-specific test datasets ready for Excel.

- Client records with Brazilian names, valid CPF, and mobile numbers
- Purchase records referencing existing clients
- Exports to CSV and XLSX (Excel)

This repo contains two modules: a Client generator and a Purchase generator.

## Requirements

- Python 3.8+
- pip (Python package manager)

Python packages used:
- Faker (locale `pt_BR`) — realistic names
- validate-docbr — valid CPF generation
- openpyxl — Excel `.xlsx` export

Install dependencies:
```
python -m pip install faker validate-docbr openpyxl
```
(Optional) Use a virtual environment if you want isolation from your system Python.

## Quick Start

1) Generate clients (CSV + XLSX):
```
python scripts/gerar_clientes.py
```
Creates `clientes_ficticios.csv` and `clientes_ficticios.xlsx`.

2) Generate purchases (CSV + XLSX) referencing those clients:
```
python scripts/gerar_compras.py
```
Creates `compras.csv` and `compras.xlsx`.

---

## Module: Client Generator

Script: `scripts/gerar_clientes.py`

Generates a database of Brazilian clients with the following columns:
- `CódigoCliente`: sequential code `c00001`, `c00002`, ...
- `NomeCompleto`: realistic Portuguese (Brazil) full name
- `Celular`: Brazilian mobile format `(DD) 9XXXX-XXXX`
- `CPF`: valid CPF with mask `XXX.XXX.XXX-YY`
- `Email`: derived from the name (`primeiro.sobrenome@example.com`), unique in the file

Command syntax:
```
python scripts/gerar_clientes.py [count] [out.csv] [out.xlsx]
```
Parameters:
- `count` (optional): number of rows (default: `200`).
- `out.csv` (optional): CSV output path (default: `clientes_ficticios.csv`).
- `out.xlsx` (optional): XLSX output path (default: same as CSV with `.xlsx`).

Examples:
```
# Default (200 rows)
python scripts/gerar_clientes.py

# 1,000 rows to a custom folder
python scripts/gerar_clientes.py 1000 dados/clientes.csv dados/clientes.xlsx
```

Notes and customization:
- Email domain: inside `scripts/gerar_clientes.py`, change the `dominio` variable used when composing the email.
- DDDs: edit the `DDDS` list to restrict or expand area codes.
- Default count: adjust the default in `main()` if desired.

---

## Module: Purchase Generator

Script: `scripts/gerar_compras.py`

Creates a purchase table that references existing clients, enforcing your constraints.

Columns generated:
- `CódigoCliente`: must exist in the clients CSV
- `DataCompra`: ISO date `YYYY-MM-DD`
- `Valor`: numeric value with 2 decimals (formatted in XLSX as Brazilian currency)
- `CódigoFilial`: branch codes like `F001`, `F002`, ...

Guarantees and behavior:
- Every client present in the clients CSV receives at least one purchase.
- A client can have multiple purchases.
- If the requested total rows is less than the number of clients, the script automatically increases it so all clients have one purchase.
- Values are sampled uniformly in `[valor_min, valor_max]`.
- Dates are sampled uniformly between `inicio` and `fim` (inclusive).

Command syntax:
```
python scripts/gerar_compras.py [clients.csv] [rows] [out.csv] [out.xlsx]

Options:
  --valor-min 10.0 --valor-max 1000.0
  --inicio 2024-01-01 --fim 2024-12-31
  --filiais 5
  --seed 42
```
Parameters:
- `clients.csv` (optional): path to the clients CSV (default: `clientes_ficticios.csv`). Must contain a `CódigoCliente` column.
- `rows` (optional): total number of purchases to generate (default: `5000`). Automatically raised to the number of clients if smaller.
- `out.csv` (optional): CSV output path (default: `compras.csv`).
- `out.xlsx` (optional): XLSX output path (default: same as CSV with `.xlsx`).
- `--valor-min`, `--valor-max`: inclusive value bounds for each purchase (defaults: `50.0` and `2000.0`).
- `--inicio`, `--fim`: date range in `YYYY-MM-DD` (defaults: `2024-01-01` to `2024-12-31`).
- `--filiais`: number of branch codes to generate (default: `5`, producing `F001..F00N`).
- `--seed`: random seed to make results reproducible (default: `42`).

Examples:
```
# Default: reads clientes_ficticios.csv, writes compras.csv/.xlsx (5000 rows)
python scripts/gerar_compras.py

# 1,000 rows, custom range and branches
python scripts/gerar_compras.py clientes_ficticios.csv 1000 compras_1000.csv compras_1000.xlsx \
  --valor-min 25 --valor-max 350 --inicio 2024-06-01 --fim 2024-12-31 --filiais 7 --seed 123
```

Excel currency formatting (BR):
- In XLSX, `Valor` is written as a numeric cell with format `R$ #,##0.00`.
- On a pt-BR Excel, this displays like `R$ 1.234,56`.
- To change the format, edit `scripts/gerar_compras.py` (look for `number_format = 'R$ #,##0.00'`).

---

## Excel and Encoding Tips

- CSV: if Excel asks about encoding, choose UTF-8 to preserve accents.
- XLSX: open directly; it includes formatting for `Valor` and avoids encoding issues.

## Troubleshooting

- Python not found: try `python3` or verify your Python installation.
- pip issues: upgrade pip with `python -m pip install --upgrade pip`.
- Garbled accents in terminal previews: prefer opening the `.xlsx` or make sure your editor displays UTF-8.

## File Structure

- Client generator: `scripts/gerar_clientes.py`
- Purchase generator: `scripts/gerar_compras.py`
- Default outputs: `clientes_ficticios.csv/.xlsx`, `compras.csv/.xlsx`
