#!/bin/bash
# PM Workflow — Project Cleanup
# Removes all generated project state so you can start fresh with /pm-workflow init
#
# Usage: bash .pm/scripts/cleanup.sh

set -e

RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m'

echo ""
echo -e "${RED}╔══════════════════════════════════════════╗${NC}"
echo -e "${RED}║  PM Workflow — Project Cleanup            ║${NC}"
echo -e "${RED}║  This will DELETE all project state       ║${NC}"
echo -e "${RED}╚══════════════════════════════════════════╝${NC}"
echo ""

# Show what will be deleted
echo -e "${YELLOW}The following will be removed:${NC}"
echo ""

DIRS=(".pm" "specs" "discovery" "strategy" "validation" "delivery")
FILES_FOUND=0

for dir in "${DIRS[@]}"; do
  if [ -d "$dir" ]; then
    count=$(find "$dir" -type f 2>/dev/null | wc -l | tr -d ' ')
    echo -e "  ${RED}$dir/${NC} ($count files)"
    FILES_FOUND=$((FILES_FOUND + count))
  fi
done

if [ "$FILES_FOUND" -eq 0 ]; then
  echo -e "  ${GREEN}Nothing to clean — project is already clean.${NC}"
  echo ""
  exit 0
fi

echo ""
echo -e "  Total: ${RED}$FILES_FOUND files${NC} will be permanently deleted."
echo ""

# First confirmation
read -p "Are you sure? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
  echo -e "${GREEN}Cancelled. Nothing was deleted.${NC}"
  exit 0
fi

# Second confirmation
echo ""
echo -e "${RED}This cannot be undone. Type the project name to confirm:${NC}"

# Read project name from state if available
PROJECT_NAME=""
if [ -f ".pm/state.json" ]; then
  PROJECT_NAME=$(python3 -c "import json; print(json.load(open('.pm/state.json')).get('project_name',''))" 2>/dev/null || echo "")
fi

if [ -n "$PROJECT_NAME" ]; then
  echo -e "  Type: ${YELLOW}${PROJECT_NAME}${NC}"
  read -p "  > " CONFIRM
  if [ "$CONFIRM" != "$PROJECT_NAME" ]; then
    echo -e "${GREEN}Cancelled. Nothing was deleted.${NC}"
    exit 0
  fi
else
  read -p "  Type DELETE to confirm: " CONFIRM
  if [ "$CONFIRM" != "DELETE" ]; then
    echo -e "${GREEN}Cancelled. Nothing was deleted.${NC}"
    exit 0
  fi
fi

echo ""
echo "Cleaning up..."

# Remove directories
for dir in "${DIRS[@]}"; do
  if [ -d "$dir" ]; then
    rm -rf "$dir"
    echo -e "  ${RED}Removed${NC} $dir/"
  fi
done

echo ""
echo -e "${GREEN}Project cleaned. Run /pm-workflow init to start fresh.${NC}"
echo ""
