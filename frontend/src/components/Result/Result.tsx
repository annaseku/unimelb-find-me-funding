import { useId, useState } from 'react';
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

function formatReason(reason: string) {
  return reason.replace(/\bpostdoc_(?:0_2|2_5|5_10|10_plus)\b(?:, postdoc_(?:0_2|2_5|5_10|10_plus)\b)*/g, (stages) => {
    const ranges = stages.split(', ').map((stage) =>
      stage.replace('postdoc_', '').replace('10_plus', '10+').replace('_', '-'));
    const list = ranges.length > 2
      ? `${ranges.slice(0, -1).join(', ')}, or ${ranges.at(-1)}`
      : ranges.join(' or ');
    return `postdoc with ${list} years of experience`;
  });
}

export default function Result({ result }: { result: RankedOpportunity }) {
  const { opportunity } = result;
  const [expanded, setExpanded] = useState(false);
  const detailsId = useId();
  return <article className={styles.resultContainer}>
    <h2 className={styles.resultHeading}>
      <button className={styles.toggle} type="button" aria-expanded={expanded} aria-controls={detailsId} onClick={() => setExpanded(!expanded)}>
        <span>{opportunity.title}</span>
        <svg className={styles.toggleArrow} viewBox="0 0 32 32" aria-hidden="true" focusable="false">
          <path d="M6 11L16 21L26 11" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
      </button>
    </h2>
    <p>{opportunity.funder}</p>
    <p><strong>Closing date:</strong> {opportunity.deadline ?? 'Not specified'}</p>
    <p><strong>Funding (AUD):</strong> {opportunity.amount_aud === null ? 'Not specified' : new Intl.NumberFormat('en-AU', { style: 'currency', currency: 'AUD', maximumFractionDigits: 0 }).format(opportunity.amount_aud)}{opportunity.amount_note && ` (${opportunity.amount_note})`}</p>
    <div id={detailsId} hidden={!expanded}>
    <p>{opportunity.summary}</p>
    <div className={styles.criteria}>
      {(Object.keys(criteria) as CriterionKey[]).map((key) => <section key={key}>
        <h3>{criteria[key]}</h3>
        <p>{labels[result[key].label] ?? result[key].label.replaceAll('_', ' ')}{' · '}{Math.round(result[key].score * 100)}%</p>
        <ul>{result[key].reasons.map((reason, index) => <li key={index}>{formatReason(reason)}</li>)}</ul>
      </section>)}
    </div>
    <p><a href={opportunity.url} target="_blank" rel="noreferrer">View opportunity</a></p>
    </div>
  </article>;
}
