#!/bin/bash

# Script for compiling translations from .po to .mo files

echo "Compiling translations..."

# Compile all translations
pybabel compile -d locale

echo "Translations compiled! They are now available in the application."
