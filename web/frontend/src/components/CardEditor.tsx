import { useEffect, useRef, useState } from 'react';
import type { Card } from '../types';
import styles from './CardEditor.module.css';

interface Props {
  card: Card;
  onSave: (updates: Partial<Pick<Card, 'front' | 'back' | 'context' | 'tags'>>) => void;
  onCancel: () => void;
  isSubmitting: boolean;
}

export function CardEditor({ card, onSave, onCancel, isSubmitting }: Props) {
  const [front, setFront] = useState(card.front);
  const [back, setBack] = useState(card.back);
  const [context, setContext] = useState(card.context);
  const [tagsInput, setTagsInput] = useState(card.tags.join(', '));
  const frontRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    frontRef.current?.focus();
  }, []);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const tags = tagsInput
      .split(',')
      .map((t) => t.trim())
      .filter(Boolean);

    onSave({ front, back, context, tags });
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Escape') {
      onCancel();
    }
  };

  return (
    <form className={styles.editor} onSubmit={handleSubmit} onKeyDown={handleKeyDown}>
      <div className={styles.header}>
        <h3 className={styles.title}>Edit Card</h3>
        <span className={styles.hint}>Esc to cancel</span>
      </div>

      <div className={styles.field}>
        <label htmlFor="front" className={styles.label}>
          Question
        </label>
        <textarea
          ref={frontRef}
          id="front"
          value={front}
          onChange={(e) => setFront(e.target.value)}
          className={styles.textarea}
          rows={2}
          disabled={isSubmitting}
        />
      </div>

      <div className={styles.field}>
        <label htmlFor="back" className={styles.label}>
          Answer
        </label>
        <textarea
          id="back"
          value={back}
          onChange={(e) => setBack(e.target.value)}
          className={styles.textarea}
          rows={4}
          disabled={isSubmitting}
        />
      </div>

      <div className={styles.field}>
        <label htmlFor="context" className={styles.label}>
          Context <span className={styles.optional}>(optional)</span>
        </label>
        <textarea
          id="context"
          value={context}
          onChange={(e) => setContext(e.target.value)}
          className={styles.textarea}
          rows={3}
          disabled={isSubmitting}
        />
      </div>

      <div className={styles.field}>
        <label htmlFor="tags" className={styles.label}>
          Tags <span className={styles.optional}>(comma-separated)</span>
        </label>
        <input
          id="tags"
          type="text"
          value={tagsInput}
          onChange={(e) => setTagsInput(e.target.value)}
          className={styles.input}
          placeholder="e.g., math, algebra, concepts"
          disabled={isSubmitting}
        />
      </div>

      <div className={styles.actions}>
        <button
          type="button"
          onClick={onCancel}
          className={styles.cancelButton}
          disabled={isSubmitting}
        >
          Cancel
        </button>
        <button type="submit" className={styles.saveButton} disabled={isSubmitting}>
          {isSubmitting ? 'Saving...' : 'Save Changes'}
        </button>
      </div>
    </form>
  );
}
