/** Trailing _YYYYMMDD or _YYYYMMDD_HHMMSS stamped on by the card generator. */
const TIMESTAMP_SUFFIX = /_\d{8}(_\d{6})?$/;

/** Leading tokens that name where the material came from, not what it is about. */
const SOURCES = new Set(['3b1b', 'codesignal']);

export interface SetName {
  /** Readable words, lowercased so a column of them reads as one index. */
  title: string;
  source: string | null;
}

export function parseSetName(filename: string): SetName {
  const stem = filename.replace(/\.json$/i, '');
  const parts = stem.replace(TIMESTAMP_SUFFIX, '').split(/[-_]+/).filter(Boolean);

  if (parts.length === 0) return { title: stem, source: null };

  let source: string | null = null;
  if (parts.length > 1 && SOURCES.has(parts[0].toLowerCase())) {
    source = (parts.shift() as string).toLowerCase();
  }

  return { title: parts.join(' ').toLowerCase(), source };
}
