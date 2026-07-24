import { useNavigate } from 'react-router-dom';
import { parseSetName } from '../utils/setName';
import styles from './Summary.module.css';

interface Props {
  filename: string;
  total: number;
  added: number;
  skipped: number;
}

/** The finished deck as one bar: added, then skipped, then whatever was left. */
function OutcomeRail({
  added,
  skipped,
  remaining,
}: {
  added: number;
  skipped: number;
  remaining: number;
}) {
  const ticks = [
    ...Array.from({ length: added }, (_, i) => ['added', i] as const),
    ...Array.from({ length: skipped }, (_, i) => ['skipped', i] as const),
    ...Array.from({ length: remaining }, (_, i) => ['remaining', i] as const),
  ];
  return (
    <div className={styles.rail} aria-hidden="true">
      {ticks.map(([state, i]) => (
        <span key={`${state}-${i}`} className={styles.tick} data-state={state} />
      ))}
    </div>
  );
}

export function Summary({ filename, total, added, skipped }: Props) {
  const navigate = useNavigate();
  const remaining = total - added - skipped;
  const isFullyComplete = remaining === 0;
  const { title } = parseSetName(filename);

  return (
    <div className={styles.container}>
      <div className={styles.card}>
        <span className={styles.eyebrow}>
          {isFullyComplete ? 'Review complete' : 'Session paused'}
        </span>
        <h2 className={styles.title}>
          {isFullyComplete ? 'Every card reviewed.' : `${remaining} still waiting.`}
        </h2>
        <p className={styles.setName} title={filename}>
          {title}
        </p>

        <OutcomeRail added={added} skipped={skipped} remaining={remaining} />

        <div className={styles.stats}>
          <div className={styles.stat}>
            <span className={styles.statValue}>{added}</span>
            <span className={styles.statLabel}>Added</span>
          </div>
          <div className={styles.stat}>
            <span className={styles.statValue}>{skipped}</span>
            <span className={styles.statLabel}>Skipped</span>
          </div>
          {remaining > 0 && (
            <div className={styles.stat} data-emphasis="true">
              <span className={styles.statValue}>{remaining}</span>
              <span className={styles.statLabel}>Remaining</span>
            </div>
          )}
        </div>

        <div className={styles.actions}>
          {remaining > 0 && (
            <button
              type="button"
              onClick={() => window.location.reload()}
              className={styles.primaryButton}
            >
              Resume review
            </button>
          )}
          <button
            type="button"
            onClick={() => navigate('/review')}
            className={remaining > 0 ? styles.secondaryButton : styles.primaryButton}
          >
            {remaining > 0 ? 'Back to the desk' : 'Review another set'}
          </button>
        </div>
      </div>
    </div>
  );
}
