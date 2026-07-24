import { useCallback, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useReviewSession } from '../hooks/useReviewSession';
import type { CardWithValidation } from '../types';
import { parseSetName } from '../utils/setName';
import { CardDisplay } from './CardDisplay';
import { CardEditor } from './CardEditor';
import styles from './CardReview.module.css';
import { FileSelector } from './FileSelector';
import { Summary } from './Summary';

/** One tick per card in the deck: the whole session read at a glance. */
function DeckRail({ cards, currentIndex }: { cards: CardWithValidation[]; currentIndex: number }) {
  return (
    <div className={styles.rail} aria-hidden="true">
      {cards.map((entry, i) => (
        <span
          key={i}
          className={styles.tick}
          data-state={i === currentIndex ? 'current' : entry.card.status}
        />
      ))}
    </div>
  );
}

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
        <p className={styles.status}>Loading cards…</p>
      </div>
    );
  }

  // Error state
  if (error && cards.length === 0) {
    return (
      <div className={styles.container}>
        <div className={styles.errorCard}>
          <span className={styles.eyebrow}>Not loaded</span>
          <h2>This set would not open.</h2>
          <p>{error}</p>
          <a href="/review" className={styles.backLink}>
            Back to the desk
          </a>
        </div>
      </div>
    );
  }

  // Complete state
  if (isComplete) {
    return (
      <Summary filename={filename} total={cards.length} added={addedCount} skipped={skippedCount} />
    );
  }

  // No cards
  if (!currentCard) {
    return (
      <div className={styles.container}>
        <div className={styles.errorCard}>
          <span className={styles.eyebrow}>Empty</span>
          <h2>This set has no cards.</h2>
          <a href="/review" className={styles.backLink}>
            Back to the desk
          </a>
        </div>
      </div>
    );
  }

  const { title } = parseSetName(filename);

  return (
    <div className={styles.container}>
      <header className={styles.header}>
        <span className={styles.setName} title={filename}>
          {title}
        </span>

        <DeckRail cards={cards} currentIndex={currentIndex} />

        <div className={styles.headerRight}>
          <span className={styles.position}>
            <strong>{currentIndex + 1}</strong>
            <span className={styles.positionSep}>/</span>
            {cards.length}
          </span>
          <button
            type="button"
            onClick={refreshAnkiStatus}
            className={`${styles.ankiStatus} ${ankiStatus.connected ? styles.connected : styles.disconnected}`}
            title={ankiStatus.connected ? 'Anki connected' : 'Anki disconnected — click to retry'}
          >
            <span className={styles.ankiDot} />
            <span className={styles.ankiText}>Anki</span>
          </button>
        </div>
      </header>

      {error && (
        <div className={styles.errorToast}>
          <span>{error}</span>
          <button type="button" onClick={clearError} className={styles.dismissButton}>
            Dismiss
          </button>
        </div>
      )}

      <main className={styles.main}>
        {isEditing ? (
          <CardEditor
            card={currentCard.card}
            onSave={saveEdit}
            onCancel={cancelEditing}
            isSubmitting={isSubmitting}
          />
        ) : (
          <CardDisplay key={currentIndex} card={currentCard} />
        )}
      </main>

      {!isEditing && (
        <footer className={styles.footer}>
          <div className={styles.actions}>
            <button
              type="button"
              onClick={approve}
              disabled={isSubmitting || !ankiStatus.connected}
              className={`${styles.actionButton} ${styles.approve}`}
            >
              <span className={styles.actionLabel}>{isSubmitting ? 'Adding…' : 'Approve'}</span>
              <kbd className={styles.shortcut}>A</kbd>
            </button>

            <button
              type="button"
              onClick={startEditing}
              disabled={isSubmitting}
              className={`${styles.actionButton} ${styles.ghost}`}
            >
              <span className={styles.actionLabel}>Edit</span>
              <kbd className={styles.shortcut}>E</kbd>
            </button>

            <button
              type="button"
              onClick={skip}
              disabled={isSubmitting}
              className={`${styles.actionButton} ${styles.ghost}`}
            >
              <span className={styles.actionLabel}>Skip</span>
              <kbd className={styles.shortcut}>S</kbd>
            </button>

            <button
              type="button"
              onClick={quit}
              disabled={isSubmitting}
              className={`${styles.actionButton} ${styles.ghost}`}
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
