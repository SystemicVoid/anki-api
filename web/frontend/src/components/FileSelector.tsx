import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { listCardFiles } from '../api/client';
import type { FileStat } from '../types';
import styles from './FileSelector.module.css';

function getReviewedPercentage(file: FileStat): number {
  if (file.total_cards === 0) return 0;
  const reviewed = file.added_cards + file.skipped_cards;
  return (reviewed / file.total_cards) * 100;
}

function getStatusBadge(file: FileStat) {
  const reviewed = file.added_cards + file.skipped_cards;

  if (reviewed === 0) {
    return <span className={styles.statusBadge} data-status="new">New</span>;
  } else if (reviewed === file.total_cards) {
    return <span className={styles.statusBadge} data-status="complete">Complete</span>;
  } else {
    return <span className={styles.statusBadge} data-status="progress">In Progress</span>;
  }
}

export function FileSelector() {
  const [files, setFiles] = useState<FileStat[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

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

  const handleSelect = (filename: string) => {
    navigate(`/review?file=${encodeURIComponent(filename)}`);
  };

  if (isLoading) {
    return (
      <div className={styles.container}>
        <div className={styles.loading}>
          <div className={styles.spinner} />
          <p>Loading files...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={styles.container}>
        <div className={styles.error}>
          <span className={styles.errorIcon}></span>
          <h2>Connection Error</h2>
          <p>{error}</p>
          <button onClick={() => window.location.reload()} className={styles.retryButton}>
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      <div className={styles.content}>
        <header className={styles.header}>
          <h1 className={styles.title}>Anki Review</h1>
          <p className={styles.subtitle}>Select a card file to review</p>
        </header>

        {files.length === 0 ? (
          <div className={styles.empty}>
            <span className={styles.emptyIcon}></span>
            <h3>No card files found</h3>
            <p>
              Generate cards first using the <code>/create-anki-cards</code> command.
            </p>
          </div>
        ) : (
          <ul className={styles.fileList}>
            {files.map((file, index) => {
              return (
                <li
                  key={file.filename}
                  className={styles.fileItem}
                  style={{ animationDelay: `${index * 50}ms` }}
                >
                  <button onClick={() => handleSelect(file.filename)} className={styles.fileButton}>
                    <div className={styles.fileInfo}>
                      <div className={styles.fileHeader}>
                        <span className={styles.filename}>{file.filename}</span>
                        {getStatusBadge(file)}
                      </div>

                      <div className={styles.stats}>
                        <span className={styles.statLabel}>
                          {file.added_cards} added · {file.skipped_cards} skipped · {file.pending_cards} pending
                        </span>
                      </div>

                      <div className={styles.progressBarContainer}>
                        <div
                          className={styles.progressBar}
                          style={{ width: `${getReviewedPercentage(file)}%` }}
                        />
                      </div>
                    </div>

                    <span className={styles.fileArrow}></span>
                  </button>
                </li>
              );
            })}
          </ul>
        )}
      </div>
    </div>
  );
}
