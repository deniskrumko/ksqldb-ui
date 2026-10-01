#!/bin/bash
set -e

# Script for compiling translations from .po to .mo files

echo "Compiling translations..."

# Compile all translations
uv run --frozen pybabel compile -d locale

echo "Translations compiled! They are now available in the application."
