#!/bin/bash
PRODUCT="$1"

check_product() {
    local product="$1"
    [ "${product}" != "" ] || {
        printf "error:product is empty\n"
        exit 1
    }
}

check_python3() {
    which "python3" &>/dev/null || {
        printf "error:python3 is not found in the environment\n"
        exit 1
    }
}

main() {
    check_product "$1"
    check_python3
    [ -e .venv ] || {
        python3 -m venv .venv
    }
    source .venv/bin/activate
    pip install -U pip
    pip install -r requirements.txt
    exec python3 ./macos_restore/__main__.py "$@"
}

if [ "${BASH_SOURCE[0]}" == "$0" ]; then
    main "$@"
fi
