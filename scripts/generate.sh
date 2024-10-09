#!/usr/bin/env bash
# This script generates all output data from the input files in this repository.
#
# If executed without arguments, it downloads the required external files and
# executes all generators:
#
#     $ scripts/generate.sh
#
# The `fetch` and `generate` sub-commands can be used to execute individual
# stages:
#
#     $ scripts/generate.sh fetch
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
    [[ "$#" -eq 0 ]] && set -- all
    local cmd=$1; shift
    case "$cmd" in
    all) fetch; generate;;
    fetch) fetch "$@";;
    generate) generate "$@";;
    *) usage;;
    esac
}

usage() {
    echo >&2 <<EOF
Usage: $0 [CMD [ARG...]]

Commands:

    [all]
    fetch
    generate [MODULE...]
EOF
    return 1
}

fetch() {
    [[ "$#" -eq 0 ]] || usage
    echo == CN_2024.rdf.zip ==
    curl \
        --silent --show-error \
        --cookie-jar cookies.txt --output /dev/null \
        --data 'email=public%40showvoc.eu&password=showvoc' \
        'https://showvoc.op.europa.eu/semanticturkey/it.uniroma2.art.semanticturkey/st-core-services/Auth/login'
    curl \
        --cookie cookies.txt --output CN_2024.rdf.zip \
        'https://showvoc.op.europa.eu/semanticturkey/it.uniroma2.art.semanticturkey/st-core-services/Download/getFile?fileName=CN_2024.rdf.zip&ctx_project=ESTAT_Combined_Nomenclature%2C_2024_(CN_2024)'
    unzip -u CN_2024.rdf.zip
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
