import type { AnchorHTMLAttributes } from 'react'

function UniMelbLogo({ className, ...props }: AnchorHTMLAttributes<HTMLAnchorElement>) {
  return (
    <a 
      {...props}
      className={`logo logo--md${className ? ` ${className}` : ''}`} 
      href="https://www.unimelb.edu.au" 
      aria-label="The University of Melbourne homepage"
    >
      {/* Leave this empty. The CSS class handles rendering the logo image */}
    </a>
  );
}

export default UniMelbLogo;