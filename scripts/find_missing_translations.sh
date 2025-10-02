#!/bin/bash

# Find missing translations in messages.po files
# Handles both single-line and multiline msgstr entries

find locale/ru -name "messages.po" -type f | while read -r po_file; do
    echo "Checking $po_file"

    # Use awk to process the file and find missing translations
    awk '
    /^msgid/ {
        msgid_line = $0
        getline
        # Skip any comment lines or empty lines after msgid
        while (/^#/ || /^$/) {
            getline
        }
        # Check if this is msgstr line
        if (/^msgstr/) {
            msgstr_line = $0
            # Check if msgstr is empty (both "" and multi-line case)
            if (/^msgstr ""$/) {
                # Check next line to see if translation continues
                next_pos = getline next_line
                if (next_pos <= 0 || next_line !~ /^".*"$/) {
                    # No continuation, this is a missing translation
                    print "Missing translation at line " NR-1 ": " msgid_line
                }
            }
        }
    }
    ' "$po_file"

    echo ""
done
