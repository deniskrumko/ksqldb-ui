#!/bin/bash

# Скрипт для извлечения строк для перевода и создания .pot файла

echo "Извлекаем строки для перевода..."

# Создаем директорию locale если её нет
mkdir -p locale

# Извлекаем строки из Python файлов
pybabel extract --mapping-file=babel.cfg -o locale/messages.pot src

echo "Файл locale/messages.pot создан."

# Создаем переводы для русского языка если их нет
if [ ! -d "locale/ru/LC_MESSAGES" ]; then
    echo "Создаем файлы перевода для русского языка..."
    pybabel init -i locale/messages.pot -d locale -l ru
    echo "Создан файл locale/ru/LC_MESSAGES/messages.po"
else
    echo "Обновляем существующие переводы для русского языка..."
    pybabel update -i locale/messages.pot -d locale -l ru
    echo "Обновлен файл locale/ru/LC_MESSAGES/messages.po"
fi

# Создаем переводы для английского языка если их нет
if [ ! -d "locale/en/LC_MESSAGES" ]; then
    echo "Создаем файлы перевода для английского языка..."
    pybabel init -i locale/messages.pot -d locale -l en
    echo "Создан файл locale/en/LC_MESSAGES/messages.po"
else
    echo "Обновляем существующие переводы для английского языка..."
    pybabel update -i locale/messages.pot -d locale -l en
    echo "Обновлен файл locale/en/LC_MESSAGES/messages.po"
fi

echo "Готово! Теперь отредактируйте .po файлы и запустите scripts/compile_translations.sh"
