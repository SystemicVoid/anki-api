/** Trailing _YYYYMMDD or _YYYYMMDD_HHMMSS stamped on by the card generator. */
const TIMESTAMP_SUFFIX = /_(\d{4})(\d{2})(\d{2})(?:_(\d{2})(\d{2})(\d{2}))?$/;

/** Leading tokens that name where the material came from, not what it is about. */
const SOURCES = new Set(['3b1b', 'codesignal']);

export interface SetName {
  /** Readable words, lowercased so a column of them reads as one index. */
  title: string;
  source: string | null;
  revision: {
    /** Compact generator timestamp that distinguishes revisions in narrow rows. */
    label: string;
    /** ISO-like value suitable for a time element's dateTime attribute. */
    dateTime: string;
  } | null;
}

export function parseSetName(filename: string): SetName {
  const stem = filename.replace(/\.json$/i, '');
  const timestamp = stem.match(TIMESTAMP_SUFFIX);
  const topicStem = timestamp ? stem.slice(0, timestamp.index) : stem;
  const parts = topicStem.split(/[-_]+/).filter(Boolean);
  const [, year, month, day, hour, minute, second] = timestamp ?? [];
  const date = timestamp ? `${year}-${month}-${day}` : null;
  const time = hour && minute && second ? `${hour}:${minute}:${second}` : null;
  const compactDate = timestamp ? `${year}${month}${day}` : null;
  const compactTime = hour && minute && second ? `${hour}${minute}${second}` : null;
  const revision = date
    ? {
        label: compactTime ? `${compactDate} · ${compactTime}` : (compactDate ?? date),
        dateTime: time ? `${date}T${time}` : date,
      }
    : null;

  if (parts.length === 0) return { title: stem, source: null, revision };

  let source: string | null = null;
  if (parts.length > 1 && SOURCES.has(parts[0].toLowerCase())) {
    source = (parts.shift() as string).toLowerCase();
  }

  return { title: parts.join(' ').toLowerCase(), source, revision };
}
