#!/bin/bash

# Directory where your YAML files exist
SEARCH_DIR="k8s"

echo "🔍 Searching for YAML files in $SEARCH_DIR ..."

# Find all YAML files EXCEPT anything inside "tests" OR "jobs" folders
mapfile -t FILES < <(
    find "$SEARCH_DIR" -type f \
        \( -name "*.yaml" -o -name "*.yml" \) \
        ! -path "*/tests/*" \
        ! -path "*/jobs/*" \
        ! -path "tests/*" \
        ! -path "jobs/*" \
        | sort
)

if [ ${#FILES[@]} -eq 0 ]; then
    echo "❌ No YAML files found."
    exit 1
fi

echo
echo "📄 List of YAML files:"
echo "------------------------"

# Show the user a list with numbers
i=1
for FILE in "${FILES[@]}"; do
    echo "$i) $FILE"
    ((i++))
done

echo "A) Apply ALL YAML files"
echo

read -p "➡️  Enter file numbers to apply (e.g. 1,3,5 or A for all): " INPUT

echo
echo "🚀 Processing selection..."
echo "-----------------------------------"

# APPLY ALL OPTION
if [[ "$INPUT" == "A" || "$INPUT" == "a" ]]; then
    echo "▶️  Applying ALL YAML files..."
    for FILE in "${FILES[@]}"; do
        echo "➡️  Applying: $FILE"
        kubectl apply -f "$FILE"
        echo "-----------------------------------"
    done
    echo "✅ All files applied!"
    exit 0
fi

# Manual selection
IFS=',' read -ra SELECTED <<< "$INPUT"

for NUM in "${SELECTED[@]}"; do
    INDEX=$((NUM-1))

    if [[ $INDEX -ge 0 && $INDEX -lt ${#FILES[@]} ]]; then
        FILE="${FILES[$INDEX]}"
        echo "▶️  Applying: $FILE"
        kubectl apply -f "$FILE"
        echo "-----------------------------------"
    else
        echo "⚠️  Invalid selection: $NUM"
    fi
done

echo "✅ Done!"
