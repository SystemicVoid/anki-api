import type { CardWithValidation } from '../types';
import { ValidationWarnings } from './ValidationWarnings';
import styles from './CardDisplay.module.css';

interface Props {
  card: CardWithValidation;
  showWarnings?: boolean;
}

function isUrl(str: string): boolean {
  try {
    new URL(str);
    return true;
  } catch {
    return false;
  }
}

function formatText(text: string): React.ReactNode {
  // Split by newlines and render with line breaks
  return text.split('\n').map((line, i, arr) => (
    <span key={i}>
      {line}
      {i < arr.length - 1 && <br />}
    </span>
  ));
}

export function CardDisplay({ card, showWarnings = true }: Props) {
  const { card: cardData, warnings } = card;
  const hasContext = cardData.context.trim().length > 0;

  return (
    <article className={styles.card}>
      {/* Question */}
      <section className={styles.questionSection}>
        <span className={styles.label}>Question</span>
        <h2 className={styles.question}>{cardData.front}</h2>
      </section>

      {/* Divider */}
      <div className={styles.divider}>
        <span className={styles.dividerLine} />
      </div>

      {/* Answer */}
      <section className={styles.answerSection}>
        <span className={styles.label}>Answer</span>
        <div className={styles.answer}>{formatText(cardData.back)}</div>
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
            <div className={styles.context}>{formatText(cardData.context)}</div>
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

        {/* Source & Deck info */}
        <div className={styles.meta}>
          {cardData.source && (
            <span className={styles.metaItem}>
              <span className={styles.metaIcon}></span>
              {isUrl(cardData.source) ? (
                <a
                  href={cardData.source}
                  target="_blank"
                  rel="noopener noreferrer"
                  className={styles.sourceLink}
                >
                  {new URL(cardData.source).hostname}
                </a>
              ) : (
                <span className={styles.sourceText}>{cardData.source}</span>
              )}
            </span>
          )}
          <span className={styles.metaItem}>
            <span className={styles.metaIcon}></span>
            {cardData.deck}
          </span>
        </div>
      </footer>

      {/* Validation Warnings */}
      {showWarnings && <ValidationWarnings warnings={warnings} />}
    </article>
  );
}
