import styles from './Result.module.css';
import { criteria, type CriterionKey, type RankedOpportunity } from '../../types/funding';
const labels: Record<string, string> = {
  eligible: 'Eligible', potentially_eligible: 'Potentially eligible', unknown: 'Unknown',
  likely_ineligible: 'Likely ineligible', high: 'High', medium: 'Medium', low: 'Low',
  under_1m: 'Under $1 million', from_1m_to_2m: '$1–2 million',
  from_2m_to_5m: '$2–5 million', over_5m: '$5 million and over',
  over_60_days: 'Over 60 days', days_60_to_30: '30–60 days',
  days_30_to_15: '15–30 days', under_15_days: 'Under 15 days', closed: 'Closed',
};
export default function Result({ result }: { result: RankedOpportunity }) {
  const { opportunity } = result;

  const eligibility = result.eligibility.label;

  const eligibilityClass = eligibility === 'eligible' ? styles.eligible
                         : eligibility === 'potentially_eligible' ? styles.potentiallyEligible
                         : eligibility === 'likely_ineligible'? styles.ineligible
                         : styles.unknown;

  const funding = opportunity.amount_aud == null ? 'Not specified' : new Intl.NumberFormat('en-AU', {
          style: 'currency',
          currency: 'AUD',
          maximumFractionDigits: 0,
        }).format(opportunity.amount_aud);

  const deadline = opportunity.deadline ? new Date(`${opportunity.deadline}T00:00:00`).toLocaleDateString('en-AU', {
          day: 'numeric',
          month: 'short',
          year: 'numeric',
        })
    : 'Not specified';

  return (
    <article className={styles.resultContainer}>
      <details className={styles.resultDetails}>
        <summary className={styles.resultSummary}>
          <div className={styles.heading}>
            <h2>{opportunity.title}</h2>
            <span className={`${styles.eligibilityBadge} ${eligibilityClass}`}>
              {labels[eligibility] ?? eligibility}
            </span>
          </div>

          <p className={styles.funder}>
            {opportunity.funder}
          </p>

          <p className={styles.description}>
            {opportunity.summary}
          </p>

          <div className={styles.cardFooter}>
            <div className={styles.tags}>
              <span className={styles.tag}> Funding: {funding} </span>
              <span className={styles.tag}> Deadline: {deadline} </span>
            </div>

            <span className={styles.expandIcon} aria-hidden="true"> ▼ </span>
          </div>
        </summary>

        <div className={styles.expandedContent}>
          {opportunity.amount_note && (
            <p className={styles.amountNote}>
              Funding Notes: {opportunity.amount_note}
            </p>
          )}

          <div className={styles.criteria}>
            {(Object.keys(criteria) as CriterionKey[]).map(
              (key) => (
                <section
                  key={key}
                  className={styles.criterion}
                >
                  <h3>{criteria[key]}</h3>

                  <p className={styles.criterionScore}>
                    {labels[result[key].label] ??
                      result[key].label.replaceAll('_', ' ')}
                    {' · '}
                    {Math.round(result[key].score * 100)}%
                  </p>

                  <ul>
                    {result[key].reasons.map(
                      (reason, index) => (
                        <li key={index}>{reason}</li>
                      )
                    )}
                  </ul>
                </section>
              )
            )}
          </div>

          <a
            className={styles.opportunityLink}
            href={opportunity.url}
            target="_blank"
            rel="noopener noreferrer"
          >
            View opportunity ↗
          </a>
        </div>
      </details>
    </article>
  );
}
