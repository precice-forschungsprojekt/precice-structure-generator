#!/bin/bash

# -------------------------------------------------------------------
# Script Name: clean.sh
# Description: Deletes all files and directories in the current directory
#              except for the hardcoded preserved files.
#              Preserved files:
#                - clean.sh
#                - README.md
#                - precice-config.xml
#                - *-*/adapter-config.json
#                - *-*/run.sh
# Usage: ./clean.sh [--dry-run]
# -------------------------------------------------------------------

# Exit immediately if a command exits with a non-zero status
set -e

# Define the root directory as the current directory
ROOT_DIR="$(pwd)"

# Define the preserved files with their relative paths from ROOT_DIR
PRESERVE_FILES=(
    "clean.sh"
    "README.md"
    "precice-config.xml"
    "*-*/adapter-config.json"
    "*-*/run.sh"
)

# Define backup directory (optional)
BACKUP_DIR="$ROOT_DIR/backup_$(date '+%Y%m%d_%H%M%S')"

# Default behavior is to perform actual deletion
DRY_RUN=0

# Define log file
LOG_FILE="cleanup.log"

# Function to display a message
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

# Function to check if a relative path is in the preserved list
is_preserved() {
    local rel_path="$1"
    for preserve in "${PRESERVE_FILES[@]}"; do
        if [ "$rel_path" == "$preserve" ]; then
            return 0  # true
        fi
    done
    return 1  # false
}

# Function to delete or backup unpreserved files and directories
cleanup() {
    log "Starting cleanup in directory: $ROOT_DIR"

    # Enable dotglob to include hidden files and directories
    shopt -s dotglob

    # Iterate over all items in the root directory, including hidden ones
    for item in "$ROOT_DIR"/* "$ROOT_DIR"/.*; do
        # Get the relative path from ROOT_DIR
        rel_path="${item#$ROOT_DIR/}"

        # Handle the case when item is ROOT_DIR itself
        if [ "$rel_path" == "$ROOT_DIR" ]; then
            continue
        fi

        # Skip '.' and '..'
        if [ "$rel_path" == "." ] || [ "$rel_path" == ".." ]; then
            continue
        fi

        # Check if the item is in the preserved list
        if is_preserved "$rel_path"; then
            log "Preserving: $rel_path"
            continue
        fi

        # Check if the item is a preserved directory (e.g., 'config')
        PRESERVED_DIRS=()
        for preserve in "${PRESERVE_FILES[@]}"; do
            dir=$(dirname "$preserve")
            if [ "$dir" != "." ] && [[ ! " ${PRESERVED_DIRS[@]} " =~ " ${dir} " ]]; then
                PRESERVED_DIRS+=("$dir")
            fi
        done

        preserve_dir=false
        for dir in "${PRESERVED_DIRS[@]}"; do
            if [[ "$rel_path" == "$dir" && -d "$item" ]]; then
                preserve_dir=true
                break
            fi
        done

        if [ "$preserve_dir" = true ]; then
            log "Preserving directory: $rel_path"

            # Iterate over items inside the preserved directory
            for subitem in "$item"/* "$item"/.*; do
                # Get the relative path of the subitem
                sub_rel_path="${subitem#$ROOT_DIR/}"

                # Skip '.' and '..' inside the directory
                sub_basename="$(basename "$subitem")"
                if [ "$sub_basename" == "." ] || [ "$sub_basename" == ".." ]; then
                    continue
                fi

                # Check if the subitem is in the preserved list
                if is_preserved "$sub_rel_path"; then
                    log "Preserving: $sub_rel_path"
                    continue
                fi

                # Decide to delete or backup
                if [ "$DRY_RUN" -eq 1 ]; then
                    log "Would delete file: $sub_rel_path"
                else
                    # Create backup directory if not already
                    mkdir -p "$BACKUP_DIR"

                    if [ -f "$subitem" ] || [ -L "$subitem" ]; then
                        mv "$subitem" "$BACKUP_DIR/"
                        log "Moved file to backup: $sub_rel_path"
                    elif [ -d "$subitem" ]; then
                        mv "$subitem" "$BACKUP_DIR/"
                        log "Moved directory to backup: $sub_rel_path"
                    fi
                fi
            done
            continue  # Move to the next item in the root directory
        fi

        # If not preserved and not a preserved directory, delete or backup the item
        if [ -f "$item" ] || [ -L "$item" ]; then
            if [ "$DRY_RUN" -eq 1 ]; then
                log "Would delete file: $rel_path"
            else
                # Create backup directory if not already
                mkdir -p "$BACKUP_DIR"

                mv "$item" "$BACKUP_DIR/"
                log "Moved file to backup: $rel_path"
            fi
        elif [ -d "$item" ]; then
            if [ "$DRY_RUN" -eq 1 ]; then
                log "Would delete directory: $rel_path"
            else
                # Create backup directory if not already
                mkdir -p "$BACKUP_DIR"

                mv "$item" "$BACKUP_DIR/"
                log "Moved directory to backup: $rel_path"
            fi
        fi
    done

    # Disable dotglob after processing
    shopt -u dotglob

    if [ "$DRY_RUN" -eq 1 ]; then
        log "Dry run completed. No files were deleted or moved."
    else
        log "Cleanup completed successfully. Deleted files are backed up in '$BACKUP_DIR'."
    fi
}

# Parse optional flags
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --dry-run) DRY_RUN=1 ;;
        *) echo "Unknown parameter passed: $1"; exit 1 ;;
    esac
    shift
done

# Safety: Prompt the user before proceeding
if [ "$DRY_RUN" -eq 1 ]; then
    log "Dry run mode enabled. No files will be deleted or moved."
else
    read -p "This will delete all files and directories except the preserved ones. Are you sure you want to proceed? [y/N]: " confirm
    case "$confirm" in
        [yY][eE][sS]|[yY])
            ;;
        *)
            log "Cleanup aborted by user."
            exit 0
            ;;
    esac
fi

# Perform cleanup
cleanup
