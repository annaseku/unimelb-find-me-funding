import { useId, useState } from 'react';
import styles from './Result.module.css';
import {
  criteria,
  criterionLabel,
  type CriterionKey,
  type RankedOpportunity,
} from '../../types/funding';
export default function Result({ result }: { result: RankedOpportunity }) {
  const { opportunity } = result;
  const [expanded, setExpanded] = useState(false);
  const detailsId = useId();

  const eligibility = result.eligibility.label;

  const eligibilityClass =
    eligibility === 'eligible'
      ? styles.eligible
      : eligibility === 'potentially_eligible'
        ? styles.potentiallyEligible
        : eligibility === 'likely_ineligible'
          ? styles.ineligible
          : styles.unknown;

  const funding =
    opportunity.amount_aud == null
      ? 'Not specified'
      : new Intl.NumberFormat('en-AU', {
          style: 'currency',
          currency: 'AUD',
          maximumFractionDigits: 0,
        }).format(opportunity.amount_aud);

  const deadline = opportunity.deadline
    ? new Date(`${opportunity.deadline}T00:00:00`).toLocaleDateString('en-AU', {
        day: 'numeric',
        month: 'short',
        year: 'numeric',
      })
    : 'Not specified';

  // The title button is the disclosure control; it stretches over the whole preview so the
  // card still opens from anywhere, but its accessible name is the title alone.
  return (
    <article className={`${styles.resultContainer} ${expanded ? styles.expanded : ''}`}>
      <div className={styles.resultSummary}>
        <div className={styles.heading}>
          <h2>
            <button
              type="button"
              className={styles.toggle}
              aria-expanded={expanded}
              aria-controls={detailsId}
              onClick={() => setExpanded(!expanded)}
            >
              {opportunity.title}
            </button>
          </h2>
          <span className={`${styles.eligibilityBadge} ${eligibilityClass}`}>
            {criterionLabel(eligibility)}
          </span>
        </div>

        <p className={styles.funder}>{opportunity.funder}</p>

        <p className={styles.description}>{opportunity.summary}</p>

        <div className={styles.cardFooter}>
          <div className={styles.tags}>
            <span className={styles.tag}> Funding: {funding} </span>
            <span className={styles.tag}> Deadline: {deadline} </span>
          </div>

          <span className={styles.expandIcon} aria-hidden="true">
            {' '}
            ▼{' '}
          </span>
        </div>
      </div>

      <div id={detailsId} className={styles.expandedContent} hidden={!expanded}>
        {opportunity.amount_note && (
          <p className={styles.amountNote}>Funding Notes: {opportunity.amount_note}</p>
        )}

        <div className={styles.criteria}>
          {(Object.keys(criteria) as CriterionKey[]).map((key) => (
            <section key={key} className={styles.criterion}>
              <h3>{criteria[key]}</h3>

              <p className={styles.criterionScore}>
                {criterionLabel(result[key].label)}
                {' · '}
                {Math.round(result[key].score * 100)}%
              </p>

              <ul>
                {result[key].reasons.map((reason, index) => (
                  <li key={index}>{reason}</li>
                ))}
              </ul>
            </section>
          ))}
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
    </article>
  );
}
