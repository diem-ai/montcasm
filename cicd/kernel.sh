#!/bin/bash
# Generate custom Python Jupyter kernels.

SCRIPT="$(basename $0)"
PYTHON="python3"
VENV_KERNEL_SCRIPT="bin/kernel"


# Creates a virtual env.
# $1: venv path
function venv_create() {
    if [ ! -f "${1}/bin/activate" ]; then
        echo "[*] Creating the virtual environment '${1}'"
        mkdir -p "${1}"
        "${PYTHON}" -m venv "${1}"
    else
        echo "[*]: venv '${1}' already exists and will not be recreated"
    fi
}


# Create kernel entrypoing from a venv.
# $1: venv path
# $2: modules separated by ','
function kernel_script() {
    echo "[*] Writing kernel script as ${1}/${VENV_KERNEL_SCRIPT}"
    # Base
    echo "#!/bin/bash -li" > "${1}/${VENV_KERNEL_SCRIPT}"
    # Modules
    for mod in $(echo "${2}" | tr "," "\n"); do
        echo "module load ${mod}" >> "${1}/${VENV_KERNEL_SCRIPT}"
    done
    # Python
    echo "\$(dirname \$0)/python \"\$@\"" >> "${1}/${VENV_KERNEL_SCRIPT}"
    # Permissions
    chmod +x "${1}/${VENV_KERNEL_SCRIPT}"
}


# Registers a venv as a kernel.
# $1: venv path
# $2: kernel name
function kernel_install() {
    echo "[*] Configuring kernel virtual environment"
    source "${1}/bin/activate"
    python -m pip install -U ipykernel &>/dev/null
    echo "[*] Installing kernel"
    python -m ipykernel install --name "${2}" --user
}


# Patches a kernel definition
# $1: kernel name
function kernel_patch() {
    echo "[*] Patching kernel definition"
    local kernel_json="$(jupyter-kernelspec list | grep ${1} | awk '{print $2}')/kernel.json"
    sed -i 's|/bin/python"|/bin/kernel"|' "${kernel_json}"
}


# ---


# Setup a kernel
# $1: venv path
# $2...: modules
function do_setup() {
    # Test
    if [ -z "${1}" ]; then
        echo "Usage: ${SCRIPT} <kernel virtual environment path> [<module>,...]" >&2
        exit 1
    fi
    # Prepare
    local venv_path="${1}"
    local kernel_name="$(basename ${1})"
    local kernel_mods="${2}"
    # Run
    echo "Setting-up kernel"
    venv_create "${venv_path}"
    kernel_script "${venv_path}" "${kernel_mods}"
    kernel_install "${venv_path}" "${kernel_name}"
    kernel_patch "${kernel_name}"
}


# List kernels
function do_list() {
    jupyter-kernelspec list
}


# Remove kernel
# $1: kernel name
function do_remove() {
    if [ -z "${1}" ]; then
        echo "Usage: ${SCRIPT} remove <kernel name>" >&2
        exit 1
    fi
    # Uninstall kernel
    echo "Removing kernel"
    jupyter-kernelspec uninstall -f "${1}"
    echo "[*] The kernel virtual environment will not be removed"
}


# Entry point
case "${1}" in
    setup)
        shift
        do_setup "${@}"
        ;;
    list)
        do_list
        ;;
    remove)
        shift
        do_remove "${@}"
        ;;
    *)
        echo "Usage: ${SCRIPT} {setup|list|remove} [...]"
        exit 1
        ;;
esac
