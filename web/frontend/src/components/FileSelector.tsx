import { useCallback, useEffect, useRef, useState } from 'react';
import { Link } from 'react-router-dom';
import { listCardFiles } from '../api/client';
import type { FileStat } from '../types';
import { parseSetName } from '../utils/setName';
import { splitRelativeTime } from '../utils/time';
import styles from './FileSelector.module.css';
import { GenerateModal } from './GenerateModal';

type FileStatus = 'new' | 'in-progress' | 'complete';
type Age = 'fresh' | 'day' | 'week' | 'old';

const COMPLETED_OPEN_STORAGE_KEY = 'ankiReview.completedOpen';

const COUNT_WORDS = [
  'No',
  'One',
  'Two',
  'Three',
  'Four',
  'Five',
  'Six',
  'Seven',
  'Eight',
  'Nine',
  'Ten',
];

const UNIT_WORDS: Record<string, string> = {
  m: 'minute',
  h: 'hour',
  d: 'day',
  w: 'week',
  mo: 'month',
  y: 'year',
};

function getFileStatus(file: FileStat): FileStatus {
  const reviewed = file.added_cards + file.skipped_cards;
  if (reviewed === 0) return 'new';
  if (reviewed === file.total_cards) return 'complete';
  return 'in-progress';
}

/** How hard a waiting set is pulling: the marker's ink ramps with this. */
function getAge(file: FileStat): Age {
  const hours = (Date.now() - new Date(file.last_activity_at).getTime()) / 3600000;
  if (hours < 12) return 'fresh';
  if (hours < 48) return 'day';
  if (hours < 24 * 14) return 'week';
  return 'old';
}

function getMetadata(file: FileStat, status: FileStatus): string {
  if (status === 'new') {
    return file.total_cards === 0 ? 'empty' : `${file.total_cards} cards`;
  }
  if (status === 'in-progress') {
    return `${file.added_cards + file.skipped_cards} of ${file.total_cards}`;
  }
  if (file.skipped_cards > 0) {
    return `${file.added_cards} added · ${file.skipped_cards} skipped`;
  }
  return `${file.added_cards} added`;
}

function countWord(n: number): string {
  return n < COUNT_WORDS.length ? COUNT_WORDS[n] : String(n);
}

/** "6 hours ago" — the prose form of the same value the rail shows as "6h". */
function spellElapsed(dateString: string): string {
  const { value, unit } = splitRelativeTime(dateString);
  if (unit === '') return 'just now';
  const word = UNIT_WORDS[unit] ?? unit;
  return `${value} ${word}${value === '1' ? '' : 's'} ago`;
}

function describeQueue(
  total: number,
  waiting: FileStat[],
  reviewedCount: number
): { lead: string; tail: string } {
  if (total === 0) {
    return { lead: 'No sets yet.', tail: 'Generate one to start reviewing.' };
  }
  if (waiting.length === 0) {
    return {
      lead: 'Everything is reviewed.',
      tail: `${reviewedCount} sets sit in the archive.`,
    };
  }
  // The list arrives most-recently-active first, so the last waiting row has waited longest.
  const oldestActivity = spellElapsed(waiting[waiting.length - 1].last_activity_at);
  if (waiting.length === 1) {
    return { lead: 'One set is waiting.', tail: `It was last active ${oldestActivity}.` };
  }
  return {
    lead: `${countWord(waiting.length)} sets are waiting.`,
    tail: `The longest-waiting set was last active ${oldestActivity}.`,
  };
}

function readStoredCompletedOpen(): boolean {
  try {
    return window.localStorage.getItem(COMPLETED_OPEN_STORAGE_KEY) === 'true';
  } catch {
    return false;
  }
}

function storeCompletedOpen(open: boolean): void {
  try {
    window.localStorage.setItem(COMPLETED_OPEN_STORAGE_KEY, String(open));
  } catch {
    // The native disclosure still works when storage is unavailable.
  }
}

function FileRow({ file }: { file: FileStat }) {
  const status = getFileStatus(file);
  const { title, source, revision } = parseSetName(file.filename);
  const { value, unit } = splitRelativeTime(file.last_activity_at);
  const activityLabel = spellElapsed(file.last_activity_at);
  const activityDate = new Date(file.last_activity_at).toLocaleString();

  return (
    <li
      className={styles.row}
      data-status={status}
      data-age={status === 'complete' ? undefined : getAge(file)}
    >
      <Link
        to={`/review?file=${encodeURIComponent(file.filename)}`}
        className={styles.rowLink}
        title={file.filename}
      >
        <time
          className={styles.elapsed}
          dateTime={file.last_activity_at}
          title={`Last activity: ${activityDate}`}
        >
          <span className="sr-only">Last activity: {activityLabel}</span>
          <span className={styles.elapsedValue} aria-hidden="true">
            {value}
          </span>
          {unit && (
            <span className={styles.elapsedUnit} aria-hidden="true">
              {unit}
            </span>
          )}
        </time>

        <span className={styles.marker} aria-hidden="true" />

        <span className={styles.body}>
          <span className={styles.title}>{title}</span>
          {(source || revision) && (
            <span className={styles.identity}>
              {source && <span className={styles.source}>{source}</span>}
              {revision && (
                <time className={styles.revision} dateTime={revision.dateTime}>
                  <span className="sr-only">Revision: </span>
                  {revision.label}
                </time>
              )}
            </span>
          )}
        </span>

        <span className={styles.meta}>
          <span className={styles.metaText}>{getMetadata(file, status)}</span>
          {status === 'in-progress' && (
            <span className={styles.bar} aria-hidden="true">
              <span className={styles.barAdded} style={{ flexGrow: file.added_cards }} />
              <span className={styles.barSkipped} style={{ flexGrow: file.skipped_cards }} />
              <span className={styles.barPending} style={{ flexGrow: file.pending_cards }} />
            </span>
          )}
        </span>
      </Link>
    </li>
  );
}

export function FileSelector() {
  const [files, setFiles] = useState<FileStat[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showGenerateModal, setShowGenerateModal] = useState(false);
  const waitingFiles = files.filter((file) => getFileStatus(file) !== 'complete');
  const reviewedFiles = files.filter((file) => getFileStatus(file) === 'complete');
  const queue = describeQueue(files.length, waitingFiles, reviewedFiles.length);
  const completedDetailsRef = useRef<HTMLDetailsElement | null>(null);
  const setCompletedDetailsRef = useCallback(
    (element: HTMLDetailsElement | null) => {
      if (element !== null && completedDetailsRef.current === null) {
        element.open = waitingFiles.length === 0 || readStoredCompletedOpen();
      }
      completedDetailsRef.current = element;
    },
    [waitingFiles.length]
  );

  useEffect(() => {
    async function fetchFiles() {
      try {
        const fileList = await listCardFiles();
        setFiles(fileList);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load files');
      } finally {
        setIsLoading(false);
      }
    }
    fetchFiles();
  }, []);

  if (isLoading) {
    return (
      <main className={styles.container}>
        <div className={styles.content}>
          <p className={styles.status}>Loading sets…</p>
        </div>
      </main>
    );
  }

  if (error) {
    return (
      <main className={styles.container}>
        <div className={styles.content}>
          <div className={styles.error}>
            <span className={styles.eyebrow}>Not connected</span>
            <h1 className={styles.thesis}>The card server did not answer.</h1>
            <p className={styles.errorDetail}>{error}</p>
            <button
              type="button"
              onClick={() => window.location.reload()}
              className={styles.ghostButton}
            >
              Try again
            </button>
          </div>
        </div>
      </main>
    );
  }

  return (
    <main className={styles.container}>
      <div className={styles.content}>
        <header className={styles.masthead}>
          <div className={styles.mastheadTop}>
            <span className={styles.eyebrow}>Anki · Review desk</span>
            <button
              type="button"
              onClick={() => setShowGenerateModal(true)}
              className={styles.generateButton}
            >
              Generate cards
            </button>
          </div>
          <h1 className={styles.thesis}>
            {queue.lead} <span className={styles.thesisTail}>{queue.tail}</span>
          </h1>
        </header>

        {files.length === 0 ? null : (
          <div className={styles.sections}>
            <section aria-labelledby="waiting-heading">
              <div className={styles.sectionRule}>
                <h2 className={styles.sectionTitle} id="waiting-heading">
                  Waiting
                </h2>
                <span className={styles.ruleLine} />
                <span className={styles.sectionCount}>{waitingFiles.length}</span>
              </div>
              {waitingFiles.length > 0 ? (
                <ul className={styles.list}>
                  {waitingFiles.map((file) => (
                    <FileRow key={file.filename} file={file} />
                  ))}
                </ul>
              ) : (
                <p className={styles.status}>Nothing is waiting.</p>
              )}
            </section>

            {reviewedFiles.length > 0 && (
              <details
                className={styles.reviewed}
                ref={setCompletedDetailsRef}
                onToggle={(event) => storeCompletedOpen(event.currentTarget.open)}
              >
                <summary className={styles.sectionRule}>
                  <h2 className={styles.sectionTitle}>Reviewed</h2>
                  <span className={styles.ruleLine} />
                  <span className={styles.sectionCount}>{reviewedFiles.length}</span>
                  <span className={styles.chevron} aria-hidden="true" />
                </summary>
                <ul className={styles.list}>
                  {reviewedFiles.map((file) => (
                    <FileRow key={file.filename} file={file} />
                  ))}
                </ul>
              </details>
            )}
          </div>
        )}
      </div>

      <GenerateModal isOpen={showGenerateModal} onClose={() => setShowGenerateModal(false)} />
    </main>
  );
}
