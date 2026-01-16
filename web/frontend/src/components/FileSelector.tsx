import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { listCardFiles } from '../api/client';
import styles from './FileSelector.module.css';

export function FileSelector() {
  const [files, setFiles] = useState<string[]>([]);
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
            {files.map((file, index) => (
              <li
                key={file}
                className={styles.fileItem}
                style={{ animationDelay: `${index * 50}ms` }}
              >
                <button onClick={() => handleSelect(file)} className={styles.fileButton}>
                  <span className={styles.fileIcon}></span>
                  <span className={styles.fileName}>{file}</span>
                  <span className={styles.fileArrow}></span>
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
