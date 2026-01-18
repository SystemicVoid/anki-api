import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import type { FileNode } from '../types';
import { FileBrowser } from './FileBrowser';
import styles from './GenerateModal.module.css';

interface GenerateModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function GenerateModal({ isOpen, onClose }: GenerateModalProps) {
  const [inputMode, setInputMode] = useState<'url' | 'file'>('url');
  const [urlSource, setUrlSource] = useState('');
  const [selectedFile, setSelectedFile] = useState<FileNode | null>(null);
  const [tags, setTags] = useState('');
  const navigate = useNavigate();

  if (!isOpen) return null;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    const source =
      inputMode === 'url' ? urlSource.trim().replace(/^["']|["']$/g, '') : selectedFile?.path;

    if (!source) return;

    // Navigate to generation page with source and tags
    const params = new URLSearchParams({
      source: source,
    });
    if (tags.trim()) {
      params.append('tags', tags.trim());
    }

    navigate(`/generate?${params.toString()}`);
    onClose();
  };

  const isSubmitDisabled = inputMode === 'url' ? !urlSource.trim() : !selectedFile;

  const handleBackdropClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  return (
    // biome-ignore lint/a11y/noStaticElementInteractions: backdrop click-to-close is standard modal UX
    <div className={styles.backdrop} role="presentation" onClick={handleBackdropClick}>
      <div className={styles.modal}>
        <header className={styles.header}>
          <h2 className={styles.title}>Generate New Cards</h2>
          <button
            type="button"
            onClick={onClose}
            className={styles.closeButton}
            aria-label="Close modal"
          >
            ×
          </button>
        </header>

        {/* Input Mode Tabs */}
        <div className={styles.tabs}>
          <button
            type="button"
            className={inputMode === 'url' ? styles.tabActive : styles.tab}
            onClick={() => setInputMode('url')}
          >
            From URL
          </button>
          <button
            type="button"
            className={inputMode === 'file' ? styles.tabActive : styles.tab}
            onClick={() => setInputMode('file')}
          >
            From File
          </button>
        </div>

        <form onSubmit={handleSubmit} className={styles.form}>
          {/* URL Input Tab */}
          {inputMode === 'url' && (
            <div className={styles.field}>
              <label htmlFor="source" className={styles.label}>
                Source URL or File Path <span className={styles.required}>*</span>
              </label>
              <input
                id="source"
                type="text"
                value={urlSource}
                onChange={(e) => setUrlSource(e.target.value)}
                placeholder="https://example.com/article or scraped/file.md"
                className={styles.input}
                required
              />
              <p className={styles.hint}>
                Enter a URL to scrape or a path to an existing markdown file
              </p>
            </div>
          )}

          {/* File Browser Tab */}
          {inputMode === 'file' && (
            <div className={styles.field}>
              <FileBrowser selectedFile={selectedFile} onSelectFile={setSelectedFile} />
            </div>
          )}

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
            <p className={styles.hint}>Comma-separated tags to apply to generated cards</p>
          </div>

          <div className={styles.actions}>
            <button type="button" onClick={onClose} className={styles.cancelButton}>
              Cancel
            </button>
            <button type="submit" disabled={isSubmitDisabled} className={styles.generateButton}>
              Generate Cards
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
