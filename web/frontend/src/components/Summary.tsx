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

  return (
    <div className={styles.container}>
      <div className={styles.card}>
        <div className={styles.iconWrapper}>
          <span className={styles.icon}></span>
        </div>

        <h2 className={styles.title}>Review Complete</h2>
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
              <div className={styles.stat}>
                <span className={styles.statValue}>{remaining}</span>
                <span className={styles.statLabel}>Remaining</span>
              </div>
            </>
          )}
        </div>

        <div className={styles.actions}>
          <button onClick={() => navigate('/review')} className={styles.primaryButton}>
            Review Another File
          </button>
        </div>
      </div>
    </div>
  );
}
