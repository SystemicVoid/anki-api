import { MathJaxContext } from 'better-react-mathjax';
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

  return (
    <MathJaxContext config={ankiMathJaxConfig}>
      <article className={styles.card}>
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
