# Use the official image as a parent image.
FROM mcr.microsoft.com/vscode/devcontainers/base:jammy

# Install necessary tools and dependencies.
RUN curl -fsSL https://deb.nodesource.com/setup_lts.x | bash -
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends \
        python3.11 \
        python-is-python3 \
        nodejs \
        ansible \
        ansible-lint \
        git \
        zsh \
        fonts-powerline

# Switch user to container's user
USER vscode

# Install poetry
RUN curl -sSL https://install.python-poetry.org | python3 -
RUN /home/vscode/.local/bin/poetry config virtualenvs.in-project true

# Install oh-my-zsh
RUN rm -rf "$HOME/.oh-my-zsh" && sh -c "$(curl -fsSL https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"

# Install powerlevel10k
RUN git clone --depth=1 https://github.com/romkatv/powerlevel10k.git ${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/themes/powerlevel10k

# Copy zsh/omzsh settings
COPY zshrc /home/vscode/.zshrc
COPY p10k.zsh /home/vscode/.p10k.zsh
