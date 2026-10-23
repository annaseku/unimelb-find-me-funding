import { useEffect, useState } from 'react';
import { fetchStatus, statusNotice } from '../../services/fundingService';
import styles from './DataNotice.module.css';

export default function DataNotice() {
  const [notice, setNotice] = useState<string | null>(null);
  useEffect(() => {
    const request = new AbortController();
    void fetchStatus(request.signal).then((status) => {
      if (!request.signal.aborted) setNotice(statusNotice(status));
    });
    return () => request.abort();
  }, []);
  return notice ? (
    <p role="note" className={styles.notice}>
      {notice}
    </p>
  ) : null;
}
