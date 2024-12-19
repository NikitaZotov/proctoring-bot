#!/bin/bash


if ! command -v poetry &> /dev/null; then
    echo "Poetry не установлен. Устанавливаю Poetry..."
    curl -sSL https://install.python-poetry.org | python3 - || {
        echo "Ошибка установки Poetry."
        exit 1
    }
    export PATH="$HOME/.local/bin:$PATH"
fi


if ! command -v pyenv &> /dev/null; then
    echo "pyenv не установлен. Установка pyenv..."
    curl https://pyenv.run | bash || {
        echo "Ошибка установки pyenv"
        exit 1
    }
    export PATH="$HOME/.pyenv/bin:$PATH"
    eval "$(pyenv init --path)"
    eval "$(pyenv init -)"
    eval "$(pyenv virtualenv-init -)"
fi


REQUIRED_PYTHON_VERSION=$(grep -Po '(?<=python = ")[^"]+' pyproject.toml)


if ! pyenv versions | grep -q "$REQUIRED_PYTHON_VERSION"; then
    echo "Установка Python $REQUIRED_PYTHON_VERSION через pyenv..."
    pyenv install "$REQUIRED_PYTHON_VERSION" || {
        echo "Ошибка установки Python $REQUIRED_PYTHON_VERSION"
        exit 1
    }
fi


echo "Настройка Python $REQUIRED_PYTHON_VERSION для проекта..."
pyenv local "$REQUIRED_PYTHON_VERSION"


echo "Установка зависимости через Poetry..."
poetry install || {
    echo "Ошибка установки зависимостей через Poetry"
    exit 1
}

echo "Активация виртуального окружения..."
source "$(poetry env info --path)/bin/activate"

echo "Все зависимости установлены, окружение активировано"

