#!/bin/sh

# Exit immediately if a command exits with a non-zero status.
set -e

# --- Configuration & Color Definitions ---
RED='\033[1;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
GREEN='\033[1;32m'
CYAN='\033[1;36m'
NC='\033[0m' # No Color

SCRIPT_NAME="[EDU_ENTRYPOINT]"
HOST_BACKEND_MOUNT_ROOT="/home/user/Edulite/backend"
DJANGO_PROJECT_SUBDIR="EduLite"
ACTUAL_DJANGO_PROJECT_DIR="${HOST_BACKEND_MOUNT_ROOT}/${DJANGO_PROJECT_SUBDIR}"
VENV_DIR="${HOST_BACKEND_MOUNT_ROOT}/venv"
VENV_PYTHON_EXEC="${VENV_DIR}/bin/python"
VENV_PIP_EXEC="${VENV_DIR}/bin/pip"
VENV_ACTIVATE_SCRIPT="${VENV_DIR}/bin/activate"

echo "${BLUE}${SCRIPT_NAME} Starting EduLite Backend Service...${NC}"

# --- 1. Sanity Check: Django Project Files ---
echo "${BLUE}${SCRIPT_NAME} Verifying Django project structure...${NC}"
if [ ! -d "${ACTUAL_DJANGO_PROJECT_DIR}" ] || [ ! -f "${ACTUAL_DJANGO_PROJECT_DIR}/manage.py" ]; then
    echo "${RED}${SCRIPT_NAME} CRITICAL ERROR: Django project structure invalid.${NC}" >&2
    exit 1
fi
echo "${GREEN}${SCRIPT_NAME} Django project structure seems OK.${NC}"


# --- 2. Virtual Environment Setup & Verification ---
echo "${BLUE}${SCRIPT_NAME} Managing Python virtual environment at ${VENV_DIR}...${NC}"

# Check if venv is not just present, but healthy (python and pip executables exist)
NEEDS_VENV_RECREATION=false
if [ ! -f "$VENV_ACTIVATE_SCRIPT" ] || [ ! -x "$VENV_PYTHON_EXEC" ] || [ ! -x "$VENV_PIP_EXEC" ]; then
    echo "${YELLOW}${SCRIPT_NAME} Virtual environment at ${VENV_DIR} is missing, incomplete, or key executables not found/executable.${NC}"
    NEEDS_VENV_RECREATION=true
else
    # Venv exists, try a quick test if pip is really working
    echo "${CYAN}${SCRIPT_NAME} Virtual environment found. Verifying pip usability...${NC}"
    if ! "$VENV_PIP_EXEC" --version > /dev/null 2>&1; then
        echo "${YELLOW}${SCRIPT_NAME} Existing venv pip at '${VENV_PIP_EXEC}' is not working. Flagging for recreation.${NC}"
        NEEDS_VENV_RECREATION=true
    else
        echo "${GREEN}${SCRIPT_NAME} Existing venv pip seems OK.${NC}"
    fi
fi

if [ "$NEEDS_VENV_RECREATION" = true ]; then
    echo "${CYAN}${SCRIPT_NAME} Attempting to (re)create virtual environment...${NC}"
    # Ensure parent directory of VENV_DIR is writable
    if ! mkdir -p "$(dirname "$VENV_DIR")" 2>/dev/null && [ ! -d "$(dirname "$VENV_DIR")" ]; then
        echo "${RED}${SCRIPT_NAME} CRITICAL ERROR: Cannot create parent directory for venv ${VENV_DIR}.${NC}" >&2
        exit 1
    fi
    if ! touch "${HOST_BACKEND_MOUNT_ROOT}/.writable_test" 2>/dev/null; then
        echo "${RED}${SCRIPT_NAME} CRITICAL ERROR: Directory ${HOST_BACKEND_MOUNT_ROOT} is not writable by user '${USER}' (UID $(id -u)).${NC}" >&2
        echo "${YELLOW}${SCRIPT_NAME} Tip: Fix host volume permissions or Dockerfile user UID/GID mapping.${NC}" >&2
        exit 1
    else
        rm "${HOST_BACKEND_MOUNT_ROOT}/.writable_test" # Clean up test file
    fi

    echo "${CYAN}${SCRIPT_NAME} Removing potentially incomplete venv at ${VENV_DIR}...${NC}"
    rm -rf "$VENV_DIR"
    echo "${CYAN}${SCRIPT_NAME} Creating new virtual environment using 'python3 -m venv ${VENV_DIR}'...${NC}"
    if python3 -m venv "$VENV_DIR"; then
        echo "${GREEN}${SCRIPT_NAME} Virtual environment created successfully.${NC}"
        # Immediately verify essential executables after creation
        if [ ! -x "$VENV_PYTHON_EXEC" ]; then
            echo "${RED}${SCRIPT_NAME} CRITICAL ERROR: Python executable ('${VENV_PYTHON_EXEC}') not found in venv immediately after creation.${NC}" >&2
            exit 1
        fi
        if [ ! -x "$VENV_PIP_EXEC" ]; then
            echo "${YELLOW}${SCRIPT_NAME} pip executable ('${VENV_PIP_EXEC}') not found in venv after creation. Attempting 'ensurepip'...${NC}" >&2
            if "$VENV_PYTHON_EXEC" -m ensurepip --upgrade; then
                if [ ! -x "$VENV_PIP_EXEC" ]; then
                     echo "${RED}${SCRIPT_NAME} CRITICAL ERROR: Still no pip in venv after 'ensurepip'.${NC}" >&2
                     exit 1
                fi
                echo "${GREEN}${SCRIPT_NAME} pip ensured successfully in venv.${NC}"
            else
                echo "${RED}${SCRIPT_NAME} CRITICAL ERROR: Failed to ensure pip in venv.${NC}" >&2
                exit 1
            fi
        else
             echo "${GREEN}${SCRIPT_NAME} pip executable found in newly created venv.${NC}"
        fi
    else
        echo "${RED}${SCRIPT_NAME} CRITICAL ERROR: Failed to create virtual environment with 'python3 -m venv'.${NC}" >&2
        exit 1
    fi
fi
echo "${GREEN}${SCRIPT_NAME} Python virtual environment setup complete.${NC}"

# --- 3. Install Dependencies ---
REQUIREMENTS_FILE_PATH="${HOST_BACKEND_MOUNT_ROOT}/requirements.txt"
echo "${BLUE}${SCRIPT_NAME} Managing dependencies...${NC}"
if [ -f "$REQUIREMENTS_FILE_PATH" ]; then
    echo "${CYAN}${SCRIPT_NAME} Installing dependencies from ${REQUIREMENTS_FILE_PATH} using ${VENV_PIP_EXEC}...${NC}"
    if "$VENV_PIP_EXEC" install -r "$REQUIREMENTS_FILE_PATH"; then
        echo "${GREEN}${SCRIPT_NAME} Dependencies installed/updated successfully.${NC}"
    else
        echo "${RED}${SCRIPT_NAME} ERROR: 'pip install -r requirements.txt' failed. See output above.${NC}" >&2
        exit 1 # Dependency installation is usually critical
    fi
else
    echo "${YELLOW}${SCRIPT_NAME} Warning: 'requirements.txt' not found at ${REQUIREMENTS_FILE_PATH}. Skipping dependency installation.${NC}" >&2
fi

# --- 4. Change to Django Project Directory ---
echo "${BLUE}${SCRIPT_NAME} Changing to Django project directory: '${ACTUAL_DJANGO_PROJECT_DIR}'...${NC}"
cd "$ACTUAL_DJANGO_PROJECT_DIR" || {
    echo "${RED}${SCRIPT_NAME} CRITICAL ERROR: Failed to change directory to '${ACTUAL_DJANGO_PROJECT_DIR}'.${NC}";
    exit 1;
}
echo "${GREEN}${SCRIPT_NAME} Current directory: $(pwd)${NC}"

# --- 5. Run Django Migrations ---
echo "${BLUE}${SCRIPT_NAME} Running Django migrations using ${VENV_PYTHON_EXEC}...${NC}"
if "$VENV_PYTHON_EXEC" manage.py migrate --noinput; then
    echo "${GREEN}${SCRIPT_NAME} Django migrations completed successfully.${NC}"
else
    echo "${RED}${SCRIPT_NAME} ERROR: Django migrations failed. Check output above.${NC}" >&2
    # exit 1 # Often critical
fi

# --- 6. Start Django Development Server ---
DEFAULT_RUNSERVER_ADDRESS="0.0.0.0:8000"
exec "$VENV_PYTHON_EXEC" manage.py runserver "$DEFAULT_RUNSERVER_ADDRESS"
