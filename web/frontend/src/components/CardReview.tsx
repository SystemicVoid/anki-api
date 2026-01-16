import { useEffect, useCallback } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useReviewSession } from '../hooks/useReviewSession';
import { CardDisplay } from './CardDisplay';
import { CardEditor } from './CardEditor';
import { Summary } from './Summary';
import { FileSelector } from './FileSelector';
import styles from './CardReview.module.css';

export function CardReview() {
  const [searchParams] = useSearchParams();
  const filename = searchParams.get('file');

  const {
    cards,
    currentCard,
    currentIndex,
    addedCount,
    skippedCount,
    isComplete,
    isEditing,
    isLoading,
    isSubmitting,
    error,
    ankiStatus,
    approve,
    skip,
    quit,
    startEditing,
    cancelEditing,
    saveEdit,
    clearError,
    refreshAnkiStatus,
  } = useReviewSession(filename);

  // Keyboard shortcuts
  const handleKeyDown = useCallback(
    (e: KeyboardEvent) => {
      if (isEditing || isComplete || isLoading || isSubmitting) return;

      switch (e.key.toLowerCase()) {
        case 'a':
          if (!e.metaKey && !e.ctrlKey) {
            e.preventDefault();
            approve();
          }
          break;
        case 'e':
          if (!e.metaKey && !e.ctrlKey) {
            e.preventDefault();
            startEditing();
          }
          break;
        case 's':
          if (!e.metaKey && !e.ctrlKey) {
            e.preventDefault();
            skip();
          }
          break;
        case 'q':
          if (!e.metaKey && !e.ctrlKey) {
            e.preventDefault();
            quit();
          }
          break;
      }
    },
    [isEditing, isComplete, isLoading, isSubmitting, approve, skip, quit, startEditing]
  );

  useEffect(() => {
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [handleKeyDown]);

  // No filename - show file selector
  if (!filename) {
    return <FileSelector />;
  }

  // Loading state
  if (isLoading) {
    return (
      <div className={styles.container}>
        <div className={styles.loading}>
          <div className={styles.spinner} />
          <p>Loading cards...</p>
        </div>
      </div>
    );
  }

  // Error state
  if (error && cards.length === 0) {
    return (
      <div className={styles.container}>
        <div className={styles.errorCard}>
          <span className={styles.errorIcon}></span>
          <h2>Unable to Load Cards</h2>
          <p>{error}</p>
          <a href="/review" className={styles.backLink}>
            Back to File Selection
          </a>
        </div>
      </div>
    );
  }

  // Complete state
  if (isComplete) {
    return (
      <Summary
        filename={filename}
        total={cards.length}
        added={addedCount}
        skipped={skippedCount}
      />
    );
  }

  // No cards
  if (!currentCard) {
    return (
      <div className={styles.container}>
        <div className={styles.errorCard}>
          <span className={styles.errorIcon}></span>
          <h2>No Cards Found</h2>
          <p>This file appears to be empty.</p>
          <a href="/review" className={styles.backLink}>
            Back to File Selection
          </a>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      {/* Header with progress and status */}
      <header className={styles.header}>
        <div className={styles.progress}>
          <span className={styles.progressText}>
            Card <strong>{currentIndex + 1}</strong> of <strong>{cards.length}</strong>
          </span>
          <div className={styles.progressBar}>
            <div
              className={styles.progressFill}
              style={{ width: `${((currentIndex + 1) / cards.length) * 100}%` }}
            />
          </div>
        </div>

        <div className={styles.stats}>
          <span className={styles.stat}>
            <span className={styles.statIcon} data-type="added"></span>
            {addedCount}
          </span>
          <span className={styles.stat}>
            <span className={styles.statIcon} data-type="skipped"></span>
            {skippedCount}
          </span>
        </div>

        <button
          onClick={refreshAnkiStatus}
          className={`${styles.ankiStatus} ${ankiStatus.connected ? styles.connected : styles.disconnected}`}
          title={ankiStatus.connected ? 'Anki connected' : 'Anki disconnected - click to retry'}
        >
          <span className={styles.ankiDot} />
          <span className={styles.ankiText}>Anki</span>
        </button>
      </header>

      {/* Error toast */}
      {error && (
        <div className={styles.errorToast}>
          <span>{error}</span>
          <button onClick={clearError} className={styles.dismissButton}>
            Dismiss
          </button>
        </div>
      )}

      {/* Main content */}
      <main className={styles.main}>
        {isEditing ? (
          <CardEditor
            card={currentCard.card}
            onSave={saveEdit}
            onCancel={cancelEditing}
            isSubmitting={isSubmitting}
          />
        ) : (
          <CardDisplay card={currentCard} />
        )}
      </main>

      {/* Action buttons */}
      {!isEditing && (
        <footer className={styles.footer}>
          <div className={styles.actions}>
            <button
              onClick={approve}
              disabled={isSubmitting || !ankiStatus.connected}
              className={`${styles.actionButton} ${styles.approve}`}
            >
              <span className={styles.actionLabel}>
                {isSubmitting ? 'Adding...' : 'Approve'}
              </span>
              <kbd className={styles.shortcut}>A</kbd>
            </button>

            <button
              onClick={startEditing}
              disabled={isSubmitting}
              className={`${styles.actionButton} ${styles.edit}`}
            >
              <span className={styles.actionLabel}>Edit</span>
              <kbd className={styles.shortcut}>E</kbd>
            </button>

            <button
              onClick={skip}
              disabled={isSubmitting}
              className={`${styles.actionButton} ${styles.skip}`}
            >
              <span className={styles.actionLabel}>Skip</span>
              <kbd className={styles.shortcut}>S</kbd>
            </button>

            <button
              onClick={quit}
              disabled={isSubmitting}
              className={`${styles.actionButton} ${styles.quit}`}
            >
              <span className={styles.actionLabel}>Quit</span>
              <kbd className={styles.shortcut}>Q</kbd>
            </button>
          </div>
        </footer>
      )}
    </div>
  );
}
