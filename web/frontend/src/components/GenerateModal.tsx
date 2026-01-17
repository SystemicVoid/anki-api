import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import styles from './GenerateModal.module.css';

interface GenerateModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function GenerateModal({ isOpen, onClose }: GenerateModalProps) {
  const [source, setSource] = useState('');
  const [tags, setTags] = useState('');
  const navigate = useNavigate();

  if (!isOpen) return null;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!source.trim()) return;

    // Strip quotes from source (common when copying paths with spaces)
    const cleanSource = source.trim().replace(/^["']|["']$/g, '');

    // Navigate to generation page with source and tags
    const params = new URLSearchParams({
      source: cleanSource,
    });
    if (tags.trim()) {
      params.append('tags', tags.trim());
    }

    navigate(`/generate?${params.toString()}`);
  };

  const handleBackdropClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  return (
    <div className={styles.backdrop} onClick={handleBackdropClick}>
      <div className={styles.modal}>
        <header className={styles.header}>
          <h2 className={styles.title}>Generate New Cards</h2>
          <button
            onClick={onClose}
            className={styles.closeButton}
            aria-label="Close modal"
          >
            ×
          </button>
        </header>

        <form onSubmit={handleSubmit} className={styles.form}>
          <div className={styles.field}>
            <label htmlFor="source" className={styles.label}>
              Source URL or File Path <span className={styles.required}>*</span>
            </label>
            <input
              id="source"
              type="text"
              value={source}
              onChange={(e) => setSource(e.target.value)}
              placeholder="https://example.com/article or scraped/file.md"
              className={styles.input}
              autoFocus
              required
            />
            <p className={styles.hint}>
              Enter a URL to scrape or a path to an existing markdown file
            </p>
          </div>

          <div className={styles.field}>
            <label htmlFor="tags" className={styles.label}>
              Tags (optional)
            </label>
            <input
              id="tags"
              type="text"
              value={tags}
              onChange={(e) => setTags(e.target.value)}
              placeholder="python, decorators, advanced"
              className={styles.input}
            />
            <p className={styles.hint}>
              Comma-separated tags to apply to generated cards
            </p>
          </div>

          <div className={styles.actions}>
            <button
              type="button"
              onClick={onClose}
              className={styles.cancelButton}
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={!source.trim()}
              className={styles.generateButton}
            >
              Generate Cards
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
