import styles from './Result.module.css';
import type { FundingOpportunity } from '../../types/funding';

interface ResultProps {
  opportunity: FundingOpportunity;
}

function Result({ opportunity }: ResultProps) {
  return (
    <div className={styles.resultContainer}>
      <h5 className={styles.title}>{opportunity.title}</h5>
      <p>
        <strong>Deadline:</strong> {opportunity.deadline_raw ?? 'Not specified'}
      </p>
      <p>
        <strong>Funding:</strong> {opportunity.funding_amount_raw ?? 'Not specified'}
      </p>
      <p>
        <strong>Eligibility:</strong>{' '}
        {opportunity.eligibility_snippet ?? 'Not available'}
      </p>
      <p>
        <a href={opportunity.url} target="_blank" rel="noreferrer">
          View opportunity
        </a>
      </p>
    </div>
  );
}

export default Result;