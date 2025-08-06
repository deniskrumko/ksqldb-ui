#!/bin/bash

# Script to extract strings for translation and create .pot file

echo "Extracting strings for translation..."

# Create locale directory if it doesn't exist
mkdir -p locale

# Extract strings from Python files
pybabel extract --mapping-file=babel.cfg -o locale/messages.pot src

echo "File locale/messages.pot created."

# Create translations for Russian language if they don't exist
if [ ! -d "locale/ru/LC_MESSAGES" ]; then
    echo "Creating translation files for Russian language..."
    pybabel init -i locale/messages.pot -d locale -l ru
    echo "Created file locale/ru/LC_MESSAGES/messages.po"
else
    echo "Updating existing translations for Russian language..."
    pybabel update -i locale/messages.pot -d locale -l ru
    echo "Updated file locale/ru/LC_MESSAGES/messages.po"
fi

# Create translations for English language if they don't exist
if [ ! -d "locale/en/LC_MESSAGES" ]; then
    echo "Creating translation files for English language..."
    pybabel init -i locale/messages.pot -d locale -l en
    echo "Created file locale/en/LC_MESSAGES/messages.po"
else
    echo "Updating existing translations for English language..."
    pybabel update -i locale/messages.pot -d locale -l en
    echo "Updated file locale/en/LC_MESSAGES/messages.po"
fi

echo "Done! Now edit the .po files and run scripts/compile_translations.sh"
