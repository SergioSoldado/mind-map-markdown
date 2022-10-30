#!/usr/bin/env bash

set -e

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd "$SCRIPT_DIR" || { echo "Failed to cd to $SCRIPT_DIR" ; exit 1; }
if [ ! -d venv ]; then
  python -m venv venv
  . venv/bin/activate
  python -m pip install --upgrade pip
  python -m pip install -r requirements.txt
  pre-commit install
  deactivate
fi

cd "${SCRIPT_DIR}/backend" || { echo "Failed to cd to backend directory"; exit 1; }
if [ ! -d venv ]; then
  python -m venv venv
  . ./venv/bin/activate
  python -m pip install --upgrade pip
  python -m pip install -r requirements.txt
  deactivate
fi
