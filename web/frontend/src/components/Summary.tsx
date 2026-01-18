import { useNavigate } from 'react-router-dom';
import styles from './Summary.module.css';

interface Props {
  filename: string;
  total: number;
  added: number;
  skipped: number;
}

export function Summary({ filename, total, added, skipped }: Props) {
  const navigate = useNavigate();
  const remaining = total - added - skipped;
  const isFullyComplete = remaining === 0;

  const title = isFullyComplete ? 'Review Complete' : 'Review Session Ended';
  const icon = isFullyComplete ? '✓' : '⏸';

  return (
    <div className={styles.container}>
      <div className={styles.card}>
        <div className={styles.iconWrapper} data-complete={isFullyComplete}>
          <span className={styles.icon}>{icon}</span>
        </div>

        <h2 className={styles.title}>{title}</h2>
        {!isFullyComplete && (
          <p className={styles.subtitle}>You can resume reviewing the remaining cards anytime</p>
        )}
        <p className={styles.filename}>{filename}</p>

        <div className={styles.stats}>
          <div className={styles.stat}>
            <span className={styles.statValue}>{added}</span>
            <span className={styles.statLabel}>Added</span>
          </div>
          <div className={styles.statDivider} />
          <div className={styles.stat}>
            <span className={styles.statValue}>{skipped}</span>
            <span className={styles.statLabel}>Skipped</span>
          </div>
          {remaining > 0 && (
            <>
              <div className={styles.statDivider} />
              <div className={styles.stat} data-emphasis="true">
                <span className={styles.statValue}>{remaining}</span>
                <span className={styles.statLabel}>Remaining</span>
              </div>
            </>
          )}
        </div>

        <div className={styles.actions}>
          {remaining > 0 && (
            <button
              type="button"
              onClick={() => window.location.reload()}
              className={styles.resumeButton}
            >
              Resume Review
            </button>
          )}
          <button
            type="button"
            onClick={() => navigate('/review')}
            className={remaining > 0 ? styles.secondaryButton : styles.primaryButton}
          >
            {remaining > 0 ? 'Select Different File' : 'Review Another File'}
          </button>
        </div>
      </div>
    </div>
  );
}
