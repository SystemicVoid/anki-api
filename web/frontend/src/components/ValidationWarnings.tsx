import type { ValidationWarning } from '../types';
import styles from './ValidationWarnings.module.css';

interface Props {
  warnings: ValidationWarning[];
}

const severityIcons: Record<ValidationWarning['severity'], string> = {
  error: '',
  warning: '',
  info: '',
};

export function ValidationWarnings({ warnings }: Props) {
  if (warnings.length === 0) return null;

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <span className={styles.headerIcon}>EAT</span>
        <span className={styles.headerText}>Validation</span>
      </div>
      <ul className={styles.list}>
        {warnings.map((warning, index) => (
          <li key={index} className={`${styles.item} ${styles[warning.severity]}`}>
            <span className={styles.icon}>{severityIcons[warning.severity]}</span>
            <span className={styles.message}>{warning.message}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
