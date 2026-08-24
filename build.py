"""Gera data.js a partir do CSV de cadastro de materiais."""
import csv
import json
import re
from collections import Counter
from pathlib import Path

CSV_PATH = Path(
    r"c:\Users\Leo\Documents\Mechatronics\26. Gestão & Planejamento estratégico"
    r"\10. Controles 2026\1. RCs & Compras\Cadastro de Materiais_rev6_resumo.csv"
)
OUT_PATH = Path(__file__).parent / "data.js"

COLUMNS = [
    "item", "dataCadastro", "usuario", "cadastroCompleto", "codigo", "descricaoSimples",
    "descricaoCurta", "descricaoCompleta", "categoria", "subcategoria", "unid", "unidDetalhe",
    "ncm", "marca", "modelo", "tipoMaterial", "dimensoes", "cor", "peso", "tensao",
    "pressao", "temperatura", "certificacoes", "localArmazenagem", "estoqueMin", "estoqueMax",
    "pontoPedido", "loteMinimo", "leadTime", "condicoesArmazenamento", "custoUnitario",
    "custoEstoqueMin", "custoEstoqueMax", "fornecedor", "fornecedoresAlt", "codigoFornecedor",
    "moeda",
]


def parse_money(value: str) -> float:
    if not value or not value.strip():
        return 0.0
    s = value.replace("R$", "").strip()
    s = re.sub(r"[^\d,.-]", "", s)
    if not s or s in ("-", ""):
        return 0.0
    s = s.replace(".", "").replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return 0.0


def clean(value: str) -> str:
    return " ".join((value or "").split())


def main() -> None:
    with CSV_PATH.open("r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.reader(f, delimiter=";"))

    header = rows[1]
    summary_row = rows[0]
    items = []

    for row in rows[2:]:
        if not row or not row[0].strip().isdigit():
            continue
        while len(row) < len(header):
            row.append("")
        record = {col: clean(row[i]) if i < len(row) else "" for i, col in enumerate(COLUMNS)}
        record["custoUnitarioNum"] = parse_money(record["custoUnitario"])
        record["custoEstoqueMinNum"] = parse_money(record["custoEstoqueMin"])
        record["custoEstoqueMaxNum"] = parse_money(record["custoEstoqueMax"])
        items.append(record)

    categories = sorted({i["categoria"] for i in items if i["categoria"]})
    subcategories = sorted({i["subcategoria"] for i in items if i["subcategoria"]})
    fornecedores = sorted({i["fornecedor"] for i in items if i["fornecedor"]})
    usuarios = sorted({i["usuario"] for i in items if i["usuario"]})
    unidades = sorted({i["unid"] for i in items if i["unid"]})

    completos = sum(1 for i in items if i["cadastroCompleto"].upper() == "SIM")
    custo_min = sum(i["custoEstoqueMinNum"] for i in items)
    custo_max = sum(i["custoEstoqueMaxNum"] for i in items)

    cat_counts = Counter(i["categoria"] for i in items if i["categoria"])
    top_categorias = [{"nome": k, "qtd": v} for k, v in cat_counts.most_common(12)]

    forn_counts = Counter(i["fornecedor"] for i in items if i["fornecedor"])
    top_fornecedores = [{"nome": k, "qtd": v} for k, v in forn_counts.most_common(8)]

    payload = {
        "meta": {
            "total": len(items),
            "completos": completos,
            "pendentes": len(items) - completos,
            "custoEstoqueMin": custo_min,
            "custoEstoqueMax": custo_max,
            "categoriasCount": len(categories),
            "fonte": CSV_PATH.name,
        },
        "filtros": {
            "categorias": categories,
            "subcategorias": subcategories,
            "fornecedores": fornecedores,
            "usuarios": usuarios,
            "unidades": unidades,
        },
        "charts": {
            "categorias": top_categorias,
            "fornecedores": top_fornecedores,
        },
        "items": items,
    }

    OUT_PATH.write_text(
        "window.MATERIAIS_DATA = " + json.dumps(payload, ensure_ascii=False, indent=2) + ";\n",
        encoding="utf-8",
    )
    print(f"Gerado {OUT_PATH} com {len(items)} materiais.")


if __name__ == "__main__":
    main()
