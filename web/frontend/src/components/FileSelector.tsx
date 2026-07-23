import { useCallback, useEffect, useRef, useState } from 'react';
import { Link } from 'react-router-dom';
import { listCardFiles } from '../api/client';
import type { FileStat } from '../types';
import { formatRelativeTime } from '../utils/time';
import styles from './FileSelector.module.css';
import { GenerateModal } from './GenerateModal';

type FileStatus = 'new' | 'in-progress' | 'complete';

const COMPLETED_OPEN_STORAGE_KEY = 'ankiReview.completedOpen';

function getFileStatus(file: FileStat): FileStatus {
  const reviewed = file.added_cards + file.skipped_cards;
  if (reviewed === 0) return 'new';
  if (reviewed === file.total_cards) return 'complete';
  return 'in-progress';
}

function getReviewedPercentage(file: FileStat): number {
  const reviewed = file.added_cards + file.skipped_cards;
  return (reviewed / file.total_cards) * 100;
}

function getMetadata(file: FileStat, status: FileStatus): string {
  const reviewed = file.added_cards + file.skipped_cards;
  if (status === 'new') {
    return file.total_cards === 0 ? 'No cards found' : `Not started · ${file.total_cards} cards`;
  }
  if (status === 'complete') {
    return `All ${file.total_cards} reviewed · ${file.added_cards} added · ${file.skipped_cards} skipped`;
  }
  return `${reviewed} of ${file.total_cards} reviewed · ${file.added_cards} added · ${file.skipped_cards} skipped`;
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
  const absoluteActivity = new Date(file.last_activity_at).toLocaleString();

  return (
    <li className={styles.fileItem} data-status={status}>
      <Link to={`/review?file=${encodeURIComponent(file.filename)}`} className={styles.fileLink}>
        <span className={styles.filenameRow}>
          <span className={styles.filename} title={file.filename}>
            {file.filename.replace(/\.json$/i, '')}
          </span>
          {status === 'new' && <span className={styles.newBadge}>NEW</span>}
        </span>
        <span className={styles.metadataRow}>
          <span className={styles.metadata}>{getMetadata(file, status)}</span>
          <time
            className={styles.recency}
            dateTime={file.last_activity_at}
            title={absoluteActivity}
          >
            {formatRelativeTime(file.last_activity_at)}
          </time>
        </span>
        {status === 'in-progress' && (
          <span className={styles.progressTrack} aria-hidden="true">
            <span
              className={styles.progressFill}
              style={{ width: `${getReviewedPercentage(file)}%` }}
            />
          </span>
        )}
      </Link>
    </li>
  );
}

export function FileSelector() {
  const [files, setFiles] = useState<FileStat[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showGenerateModal, setShowGenerateModal] = useState(false);
  const activeFiles = files.filter((file) => getFileStatus(file) !== 'complete');
  const completedFiles = files.filter((file) => getFileStatus(file) === 'complete');
  const completedDetailsRef = useRef<HTMLDetailsElement | null>(null);
  const setCompletedDetailsRef = useCallback(
    (element: HTMLDetailsElement | null) => {
      if (element !== null && completedDetailsRef.current === null) {
        element.open = activeFiles.length === 0 || readStoredCompletedOpen();
      }
      completedDetailsRef.current = element;
    },
    [activeFiles.length]
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
        <div className={styles.loading}>
          <div className={styles.spinner} />
          <p>Loading files...</p>
        </div>
      </main>
    );
  }

  if (error) {
    return (
      <main className={styles.container}>
        <div className={styles.error}>
          <span className={styles.errorIcon} />
          <h2>Connection Error</h2>
          <p>{error}</p>
          <button
            type="button"
            onClick={() => window.location.reload()}
            className={styles.retryButton}
          >
            Try Again
          </button>
        </div>
      </main>
    );
  }

  return (
    <main className={styles.container}>
      <div className={styles.content}>
        <header className={styles.header}>
          <h1 className={styles.title}>Anki Review</h1>
          <p className={styles.subtitle}>Select a card file to review</p>
          <button
            type="button"
            onClick={() => setShowGenerateModal(true)}
            className={styles.generateButton}
          >
            + Generate New Cards
          </button>
        </header>

        {files.length === 0 ? (
          <div className={styles.empty}>
            <h2>No card files yet</h2>
            <p>Generate a set to start reviewing.</p>
          </div>
        ) : (
          <div className={styles.sections}>
            <section className={styles.section} aria-labelledby="active-heading">
              <header className={styles.sectionHeader}>
                <h2 className={styles.sectionTitle} id="active-heading">
                  Active <span className={styles.sectionCount}>{activeFiles.length}</span>
                </h2>
                <p className={styles.sectionSubtitle}>New and unfinished card files</p>
              </header>
              {activeFiles.length > 0 ? (
                <ul className={styles.fileList}>
                  {activeFiles.map((file) => (
                    <FileRow key={file.filename} file={file} />
                  ))}
                </ul>
              ) : (
                <p className={styles.sectionEmpty}>Nothing in progress — everything is reviewed.</p>
              )}
            </section>

            {completedFiles.length > 0 && (
              <details
                className={styles.completed}
                ref={setCompletedDetailsRef}
                onToggle={(event) => storeCompletedOpen(event.currentTarget.open)}
              >
                <summary className={styles.completedSummary}>
                  <h2 className={styles.sectionTitle}>
                    Completed <span className={styles.sectionCount}>{completedFiles.length}</span>
                  </h2>
                  <span className={styles.chevron} aria-hidden="true" />
                </summary>
                <div className={styles.completedContent}>
                  <p className={styles.sectionSubtitle}>Fully reviewed</p>
                  <ul className={styles.fileList}>
                    {completedFiles.map((file) => (
                      <FileRow key={file.filename} file={file} />
                    ))}
                  </ul>
                </div>
              </details>
            )}
          </div>
        )}
      </div>

      <GenerateModal isOpen={showGenerateModal} onClose={() => setShowGenerateModal(false)} />
    </main>
  );
}
