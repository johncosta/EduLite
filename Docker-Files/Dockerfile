FROM ubuntu:latest

# Install Git and tools to simulate Git Bash environment
RUN apt-get update && \
    apt-get install -y git curl wget nano less \
    bash-completion man-db

# Install EduLite Specific components

# ---- Python for Backend (Django) ----
RUN apt-get update && \
    apt-get install -y python3 python3-pip python3-venv && \
    rm -rf /var/lib/apt/lists/* # Clean up apt lists

# Verify installations (optional build-time checks)
RUN echo "Python version:" && python3 --version
RUN echo "pip version:" && pip3 --version

# ---- Node.js for Frontend (React + Vite) ----
# Install Node.js (e.g., LTS version)
# Using NodeSource repository for more up-to-date versions
RUN apt-get update && \
    apt-get install -y ca-certificates curl gnupg && \
    mkdir -p /etc/apt/keyrings && \
    curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg && \
    NODE_MAJOR=20 && \
    echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_$NODE_MAJOR.x nodistro main" | tee /etc/apt/sources.list.d/nodesource.list && \
    apt-get update && \
    apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/* # Clean up apt lists

# Verify installations (optional build-time checks)
RUN echo "Node version:" && node --version
RUN echo "npm version:" && npm --version

WORKDIR /home/user/edulite_frontend_app # Temporary staging directory for npm install



# Create user
ARG HOST_GID=1000 # Default to 1000 if not provided

# Create the group first, then the user. Add nogroup check for robustness.
RUN if ! getent group $HOST_GID > /dev/null 2>&1; then \
        addgroup --gid $HOST_GID usergroup; \
    else \
        echo "Group with GID $HOST_GID already exists."; \
    fi && \
    adduser --gid $HOST_GID --disabled-password --gecos "" user --no-create-home && \
    mkdir -p /home/user && \
    chown $HOST_UID:$HOST_GID /home/user
USER user
# Change to users directory
WORKDIR /home/user

# Switch to root to copy scripts to /usr/local/bin and make them executable
USER root

# Copy all scripts from in-container-scripts to /usr/local/bin
COPY in-container-scripts/django_runserver.sh /usr/local/bin/

# Make the scripts executable
RUN chmod +x /usr/local/bin/django_runserver.sh

# Set prompt and add aliases to .bashrc in a single RUN command
RUN echo 'export PS1="\[\033[01;32m\]\u@\h\[\033[00m\]:\[\033[01;34m\]\w\[\033[00m\]\$ "' >> ~/.bashrc && \
    echo "alias pmrs='/usr/local/bin/django_runserver.sh || true'" >> ~/.bashrc

# Switch back to the user
USER user
# Set the default command to run the intro script, which then execs bash
CMD ["/usr/local/bin/container_intro.sh", "/bin/bash"]
