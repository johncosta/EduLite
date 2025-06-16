#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e
# Treat unset variables as an error when substituting.
set -u

# --- Configuration (with defaults, can be overridden by environment variables) ---
EDULITE_PROJECT_NAME="${EDULITE_PROJECT_NAME:-edulite}"

# The Docker Compose file(s) to use.
EDULITE_COMPOSE_FILES_ARGS=() # Initialize as an array
DEFAULT_COMPOSE_FILE="docker-compose.yml"
ADDITIONAL_COMPOSE_FILE="${EDULITE_COMPOSE_OVERRIDE_FILE:-docker-compose.override.yml}" # Common override file

# Construct docker-compose file arguments
if [ -f "$DEFAULT_COMPOSE_FILE" ]; then
    EDULITE_COMPOSE_FILES_ARGS+=("-f" "$DEFAULT_COMPOSE_FILE")
else
    echo "Warning: Default Docker Compose file '$DEFAULT_COMPOSE_FILE' not found."
    # Allow proceeding if an override or specific compose file is intended to be the primary
fi

if [ -f "$ADDITIONAL_COMPOSE_FILE" ]; then
    EDULITE_COMPOSE_FILES_ARGS+=("-f" "$ADDITIONAL_COMPOSE_FILE")
fi

if [ ${#EDULITE_COMPOSE_FILES_ARGS[@]} -eq 0 ]; then
    echo "Error: No Docker Compose files found ('$DEFAULT_COMPOSE_FILE' or '$ADDITIONAL_COMPOSE_FILE'). Please ensure at least one exists or specify via EDULITE_COMPOSE_FILES."
    # If EDULITE_COMPOSE_FILES is set as a string of "-f file1 -f file2", it could be used too.
    # For simplicity, this script focuses on default and override.
    exit 1
fi

# The primary service name in your docker-compose.yml to attach to, view logs for, etc.
EDULITE_MAIN_SERVICE="${EDULITE_MAIN_SERVICE:-backend}"

# Base docker-compose command with project name and file arguments
# docker compose v2 syntax
DOCKER_COMPOSE_CMD="docker compose -p ${EDULITE_PROJECT_NAME} ${EDULITE_COMPOSE_FILES_ARGS[*]}"
# --- Helper Functions ---

# Function to display usage
usage() {
  echo "EduLite Development Environment Management (Docker Compose)"
  echo "---------------------------------------------------------"
  echo "Usage: ./containers.sh [option]"
  echo
  echo "Configuration (via environment variables):"
  echo "  EDULITE_PROJECT_NAME: Docker Compose project name (default: ${EDULITE_PROJECT_NAME})"
  echo "  EDULITE_COMPOSE_FILES: Path to your Docker Compose file(s) (default: \"${EDULITE_COMPOSE_FILES_ARGS[*]}\")"
  echo "  EDULITE_MAIN_SERVICE: Main service to attach/log (default: ${EDULITE_MAIN_SERVICE})"
  echo
  echo "Options:"
  echo "  up        - Start all services (create if not exists, build if needed)"
  echo "  shell     - Attach to the main service's shell (${EDULITE_MAIN_SERVICE})"
  echo "  down      - Stop and remove all services, networks, and optionally volumes"
  echo "  stop      - Stop all services (without removing them)"
  echo "  restart   - Restart all services"
  echo "  build     - Build or rebuild services"
  echo "  logs      - View logs from the main service (${EDULITE_MAIN_SERVICE})"
  echo "  status    - Check service status and more details"
  echo "  clean     - Stop and remove services, networks, AND volumes (destructive)"
  echo "  help      - Show this message"
  echo
}

# Check if Docker daemon is running
check_docker_daemon() {
  if ! docker info > /dev/null 2>&1; then
    echo "Error: Docker daemon is not running. Please start Docker and try again."
    exit 1
  fi
  if ! docker-compose --version > /dev/null 2>&1; then
    echo "Error: docker-compose is not installed or not in PATH. Please install it."
    exit 1
  fi
}

# Check if any services are running for the project
services_running() {
  # Count running containers for the project
  local running_services_count
  running_services_count=$($DOCKER_COMPOSE_CMD ps -q | wc -l | tr -d ' ') # Get count of running service containers
  if [ "$running_services_count" -gt 0 ]; then
    return 0 # True, services are running
  else
    return 1 # False, no services running
  fi
}

# --- Main Functions ---

start_services() {
  echo "Starting all services for project '${EDULITE_PROJECT_NAME}'..."
  echo "Using Docker Compose files: ${EDULITE_COMPOSE_FILES_ARGS[*]}"
  echo "This may build images if they don't exist or if specified in compose file."
  $DOCKER_COMPOSE_CMD up -d --remove-orphans # Start in detached mode, remove orphan containers
  echo "Services started. Use 'status' to check, 'logs' to view output, 'shell' to connect."
}

attach_to_service_shell() {
  if ! services_running; then
    echo "Services for project '${EDULITE_PROJECT_NAME}' are not running. Use 'up' first."
    read -p "Would you like to start the services now? (y/N): " confirm
    if [[ "$confirm" == [yY] || "$confirm" == [yY][eE][sS] ]]; then
      start_services
    else
      exit 1
    fi
  fi
  echo "Attaching to '${EDULITE_MAIN_SERVICE}' service shell for project '${EDULITE_PROJECT_NAME}'..."
  # Assuming the service has bash. Adjust if it uses sh or another shell.
  $DOCKER_COMPOSE_CMD exec "${EDULITE_MAIN_SERVICE}" bash
}

stop_services() {
  echo "Stopping all services for project '${EDULITE_PROJECT_NAME}'..."
  $DOCKER_COMPOSE_CMD stop
  echo "Services stopped."
}

down_services() {
  echo "Stopping and removing containers and networks for project '${EDULITE_PROJECT_NAME}'..."
  echo "Volumes will NOT be removed by default. Use 'clean' for that."
  $DOCKER_COMPOSE_CMD down --remove-orphans
  echo "Services, containers, and networks removed."
}

clean_services() {
  echo "WARNING: This will stop and remove services, networks, AND ALL VOLUMES for project '${EDULITE_PROJECT_NAME}'."
  read -p "Are you sure you want to proceed? This is destructive. (y/N): " confirm
  if [[ "$confirm" == [yY] || "$confirm" == [yY][eE][sS] ]]; then
    echo "Proceeding with full clean..."
    $DOCKER_COMPOSE_CMD down -v --remove-orphans # -v removes named volumes
    echo "All services, networks, and volumes for project '${EDULITE_PROJECT_NAME}' have been removed."
  else
    echo "Clean operation aborted."
  fi
}

build_services() {
  echo "Building or rebuilding services for project '${EDULITE_PROJECT_NAME}'..."
  echo "This will use build instructions in your Docker Compose file(s)."
  # Add --build-arg for UID and GID
  local current_uid=$(id -u)
  local current_gid=$(id -g)
  echo "Using HOST_UID=${current_uid} and HOST_GID=${current_gid} for build."
  $DOCKER_COMPOSE_CMD build \
    --build-arg HOST_UID="${current_uid}" \
    --build-arg HOST_GID="${current_gid}" \
    "$@" # Pass any additional args (e.g., service name, --no-cache)
  echo "Build process completed."
  echo "You may want to run './containers.sh up --force-recreate' to use the new images."
}

restart_services() {
    echo "Restarting all services for project '${EDULITE_PROJECT_NAME}'..."
    $DOCKER_COMPOSE_CMD restart
    echo "Services restarted."
}

view_logs() {
  echo "Viewing logs for service '${EDULITE_MAIN_SERVICE}' in project '${EDULITE_PROJECT_NAME}'..."
  echo "Use Ctrl+C to stop viewing logs."
  $DOCKER_COMPOSE_CMD logs -f --tail="100" "${EDULITE_MAIN_SERVICE}" "$@" # Follow logs, show last 100 lines, allow extra args
}

show_status() {
  echo "Status for Docker Compose project '${EDULITE_PROJECT_NAME}':"
  echo "--- Services Status (docker-compose ps) ---"
  $DOCKER_COMPOSE_CMD ps
  echo
  echo "--- Docker Images Used (from compose config) ---"
  $DOCKER_COMPOSE_CMD config --images
  echo
  if services_running; then
    echo "--- Recent logs from '${EDULITE_MAIN_SERVICE}' (last 10 lines) ---"
    $DOCKER_COMPOSE_CMD logs --tail="10" "${EDULITE_MAIN_SERVICE}"
    echo
    echo "--- Network(s) ---"
    docker network ls | grep "${EDULITE_PROJECT_NAME}" || echo "No project-specific networks found (or name mismatch)."
  else
    echo "Services are not running. No logs or detailed network info to display."
  fi
}

# --- Script Execution ---

# Always check if Docker is running first
check_docker_daemon

# Default action: if no arguments, try to start (if not running) and then attach.
if [ $# -eq 0 ]; then
  if ! services_running; then
    echo "No services running for project '${EDULITE_PROJECT_NAME}'. Starting them now..."
    start_services
  fi
  attach_to_service_shell
  exit 0
fi

# Process command line arguments
case "$1" in
  up)
    shift # Remove 'up'
    start_services "$@" # Pass remaining args to docker-compose up
    ;;
  shell|attach) # 'attach' as an alias for 'shell'
    shift
    attach_to_service_shell "$@"
    ;;
  down)
    shift
    down_services "$@"
    ;;
  stop)
    shift
    stop_services "$@"
    ;;
  restart)
    shift
    restart_services "$@"
    ;;
  build)
    shift
    build_services "$@"
    ;;
  logs)
    shift
    view_logs "$@"
    ;;
  status)
    shift
    show_status "$@"
    ;;
  clean)
    shift
    clean_services "$@"
    ;;
  help|--help|-h)
    usage
    ;;
  *)
    echo "Unknown option: $1"
    usage
    exit 1
    ;;
esac
