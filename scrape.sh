#!/usr/bin/env bash
#
# Scrape wrapper for anki-api
# Calls crawl4ai scraper with non-interactive flags
#
# Usage: ./scrape.sh <url>
#
# Exit codes:
#   0 - Success
#   1 - Scraping failed
#   2 - Invalid arguments

set -e
set -o pipefail

CRAWL4AI_DIR="/home/hugo/Documents/Engineering/crawl4ai"
ANKI_API_DIR="$(cd "$(dirname "$0")" && pwd)"
SCRAPED_DIR="${ANKI_API_DIR}/scraped"

# Check if URL provided
if [ $# -eq 0 ]; then
    echo "Usage: ./scrape.sh <url>" >&2
    echo "Example: ./scrape.sh https://example.com/article" >&2
    exit 2
fi

URL="$1"

# Ensure scraped directory exists
mkdir -p "${SCRAPED_DIR}"

echo "Scraping: ${URL}"
echo "Output directory: ${SCRAPED_DIR}/"
echo ""

# Run crawl4ai scraper with non-interactive flags
# The scraper will output only the file path in quiet mode
cd "${CRAWL4AI_DIR}"
if ! SCRAPED_FILE=$(uv run scrape_to_markdown.py "${URL}" \
    --output-dir "${SCRAPED_DIR}" \
    --non-interactive \
    --quiet) || [ -z "${SCRAPED_FILE}" ]; then
    echo "Error: Scraping failed" >&2
    exit 1
fi

# Extract just the filename for display
FILENAME=$(basename "${SCRAPED_FILE}")

echo ""
echo "✓ Scraped content saved to: scraped/${FILENAME}"
echo ""
echo "Next steps:"
echo "  1. Read the content: cat scraped/${FILENAME}"
echo "  2. Generate flashcards: /create-anki-cards"
echo "  3. Review cards: uv run anki review cards/your-cards.json"
