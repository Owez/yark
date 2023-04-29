#!/bin/bash

if [[ -f poetry.lock ]]; then
    sudo poetry config virtualenvs.create false
    sudo poetry install --no-interaction --no-root
fi
