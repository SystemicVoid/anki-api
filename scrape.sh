#!/usr/bin/env bash
#
# Scrape wrapper for anki-api
# Calls crawl4ai scraper and copies output to anki-api/scraped/
#
# Usage: ./scrape.sh <url>

set -e

CRAWL4AI_DIR="/home/hugo/Documents/Engineering/crawl4ai"
ANKI_API_DIR="$(cd "$(dirname "$0")" && pwd)"
SCRAPED_DIR="${ANKI_API_DIR}/scraped"

# Check if URL provided
if [ $# -eq 0 ]; then
    echo "Usage: ./scrape.sh <url>"
    echo "Example: ./scrape.sh https://example.com/article"
    exit 1
fi

URL="$1"

# Ensure scraped directory exists
mkdir -p "${SCRAPED_DIR}"

echo "Scraping: ${URL}"
echo "Output will be saved to: ${SCRAPED_DIR}/"
echo ""

# Run crawl4ai scraper
cd "${CRAWL4AI_DIR}"
uv run scrape_to_markdown.py "${URL}"

# Find the most recent markdown file in crawl4ai's scraped directory
LATEST=$(find "${CRAWL4AI_DIR}/scraped" -name "*.md" -type f -printf '%T@ %p\n' | sort -rn | head -1 | cut -d' ' -f2-)

if [ -z "${LATEST}" ]; then
    echo "Error: No markdown file found in ${CRAWL4AI_DIR}/scraped/"
    exit 1
fi

FILENAME=$(basename "${LATEST}")

# Copy to anki-api scraped directory
cp "${LATEST}" "${SCRAPED_DIR}/${FILENAME}"

echo ""
echo "✓ Scraped content saved to: scraped/${FILENAME}"
echo ""
echo "Next steps:"
echo "  1. Read the content: cat scraped/${FILENAME}"
echo "  2. Generate flashcards (use coding agent)"
echo "  3. Review cards: uv run anki review cards/your-cards.json"
