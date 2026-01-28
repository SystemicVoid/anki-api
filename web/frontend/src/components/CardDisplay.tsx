import { MathJaxContext } from 'better-react-mathjax';
import { useCallback, useState } from 'react';
import { ankiMathJaxConfig } from '../mathjaxConfig';
import type { CardWithValidation } from '../types';
import styles from './CardDisplay.module.css';
import { MathJaxContent } from './MathJaxContent';

interface Props {
  card: CardWithValidation;
}

export function CardDisplay({ card }: Props) {
  const { card: cardData } = card;
  const hasContext = cardData.context.trim().length > 0;
  const [copied, setCopied] = useState(false);

  const copyCardText = useCallback(async () => {
    const parts = [`Q: ${cardData.front}`, `A: ${cardData.back}`];
    if (cardData.context.trim()) {
      parts.push(`Context: ${cardData.context}`);
    }
    const fullText = parts.join('\n\n');

    try {
      await navigator.clipboard.writeText(fullText);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // Fallback for older browsers
      const textarea = document.createElement('textarea');
      textarea.value = fullText;
      document.body.appendChild(textarea);
      textarea.select();
      document.execCommand('copy');
      document.body.removeChild(textarea);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  }, [cardData]);

  return (
    <MathJaxContext config={ankiMathJaxConfig}>
      <article className={styles.card}>
        {/* Copy button */}
        <button
          type="button"
          onClick={copyCardText}
          className={`${styles.copyButton} ${copied ? styles.copied : ''}`}
          title="Copy card text"
          aria-label={copied ? 'Copied!' : 'Copy card text'}
        >
          <svg
            className={styles.copyIcon}
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            aria-hidden="true"
          >
            {copied ? (
              <path className={styles.checkPath} d="M5 12l5 5L20 7" />
            ) : (
              <>
                <rect x="9" y="9" width="13" height="13" rx="2" />
                <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" />
              </>
            )}
          </svg>
        </button>
        {/* Question */}
        <section className={styles.questionSection}>
          <span className={styles.label}>
            Question
            {cardData.anki_id && (
              <span className={styles.addedBadge} title="Already added to Anki">
                ✓ Added
              </span>
            )}
          </span>
          <h2 className={styles.question}>
            <MathJaxContent text={cardData.front} />
          </h2>
        </section>

        {/* Divider */}
        <div className={styles.divider}>
          <span className={styles.dividerLine} />
        </div>

        {/* Answer */}
        <section className={styles.answerSection}>
          <span className={styles.label}>Answer</span>
          <div className={styles.answer}>
            <MathJaxContent text={cardData.back} />
          </div>
        </section>

        {/* Context */}
        {hasContext && (
          <>
            <div className={styles.contextDivider}>
              <span className={styles.contextDividerLine} />
              <span className={styles.contextDividerText}>Context</span>
              <span className={styles.contextDividerLine} />
            </div>
            <section className={styles.contextSection}>
              <div className={styles.context}>
                <MathJaxContent text={cardData.context} />
              </div>
            </section>
          </>
        )}

        {/* Metadata */}
        <footer className={styles.footer}>
          {/* Tags */}
          {cardData.tags.length > 0 && (
            <div className={styles.tags}>
              {cardData.tags.map((tag, i) => (
                <span key={i} className={styles.tag}>
                  {tag}
                </span>
              ))}
            </div>
          )}
        </footer>
      </article>
    </MathJaxContext>
  );
}
