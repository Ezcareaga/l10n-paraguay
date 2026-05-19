#!/usr/bin/env bash
# scripts/setup_references.sh — Clona los repos de referencia para codegraph.
#
# Tras correr este script, ejecutar:
#   python scripts/build_index.py
# para construir el índice consultable vía bin/codegraph.

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
REF_DIR="$REPO_ROOT/references"

mkdir -p "$REF_DIR"
cd "$REF_DIR"

clone_if_missing() {
    local dir="$1" url="$2" branch="${3:-}"
    if [ -d "$dir" ]; then
        echo "[skip] $dir already exists"
        return
    fi
    echo "[clone] $dir ${branch:+(branch $branch)}"
    if [ -n "$branch" ]; then
        git clone --depth 1 --branch "$branch" "$url" "$dir"
    else
        git clone --depth 1 "$url" "$dir"
    fi
}

# Odoo 18 (sparse) — el más pesado, ~150 MB después de sparse
if [ ! -d "odoo-18.0" ]; then
    echo "[clone] odoo-18.0 (sparse — solo addons clave)"
    git clone --depth 1 --branch 18.0 --filter=blob:none --sparse https://github.com/odoo/odoo odoo-18.0
    (
        cd odoo-18.0
        git sparse-checkout set \
            addons/account \
            addons/account_edi \
            addons/account_edi_ubl_cii \
            addons/l10n_latam_base \
            addons/l10n_latam_invoice_document \
            addons/l10n_pe \
            addons/l10n_ec \
            addons/l10n_ar \
            addons/l10n_cl \
            addons/l10n_co \
            addons/l10n_mx \
            addons/point_of_sale \
            addons/stock \
            addons/product
    )
else
    echo "[skip] odoo-18.0 already exists"
fi

clone_if_missing "nandefact"                "https://github.com/Ezcareaga/nandefact"            ""
clone_if_missing "l10n-peru"                "https://github.com/OCA/l10n-peru"                  "18.0"
clone_if_missing "l10n-ecuador"             "https://github.com/OCA/l10n-ecuador"               "18.0"
clone_if_missing "l10n-argentina"           "https://github.com/OCA/l10n-argentina"             "18.0"
clone_if_missing "l10n-brazil"              "https://github.com/OCA/l10n-brazil"                "18.0"
clone_if_missing "oca-addons-repo-template" "https://github.com/OCA/oca-addons-repo-template"   ""

# Branches viejas — útiles porque OCA aún no portó muchos addons a 18.0
clone_if_missing "l10n-ecuador-17.0"        "https://github.com/OCA/l10n-ecuador"               "17.0"
clone_if_missing "l10n-argentina-16.0"      "https://github.com/OCA/l10n-argentina"             "16.0"

echo ""
echo "=== References ready. Run next: ==="
echo "  python scripts/build_index.py"
