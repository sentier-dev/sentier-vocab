#!/usr/bin/env bash
# This script generates all output data from the input files in this repository.
#
# If executed without arguments, it executes all generators:
#
#     $ scripts/generate.sh
#
# The `generate` sub-commands can be used to execute individual stages:
#
#     $ scripts/generate.sh generate nace
set -euo pipefail

GENERATORS=(
    combined_nomenclature
    custom_products
    envo
    model_terms
    nace
    open_energy_ontology
    qudt
    supplements
)

declare -A GENERATOR_ARGS
GENERATOR_ARGS=(
    [combined_nomenclature]=sentier_vocab/CN_2024.rdf
    [nace]=sentier_vocab/CN_2024.rdf
)

main() {
    [[ "$#" -eq 0 ]] && set -- generate
    local cmd=$1; shift
    case "$cmd" in
    generate) generate "$@";;
    *) usage;;
    esac
}

usage() {
    echo >&2 <<EOF
Usage: $0 [CMD [ARG...]]

Commands:

    generate [MODULE...]
EOF
    return 1
}

generate() {
    [[ "$#" -eq 0 ]] && set -- "${GENERATORS[@]}"
    local x
    for x; do
        echo "== $x =="
        python -m "sentier_vocab.$x" ${GENERATOR_ARGS[$x]-}
    done
}

main "$@"
