import { useId } from "react";
import "../../styles/empty-state.css";

export interface EmptyStateProps {
  title: string;
  description: string;
  action?: {
    label: string;
    onClick: () => void;
  };
  headingLevel?: 2 | 3 | 4;
  className?: string;
}

export function EmptyState({
  title,
  description,
  action,
  headingLevel = 2,
  className = "",
}: EmptyStateProps) {
  const titleId = useId();
  const classNames = ["empty-state", className].filter(Boolean).join(" ");
  const Heading = headingLevel === 4 ? "h4" : headingLevel === 3 ? "h3" : "h2";

  return (
    <section className={classNames} aria-labelledby={titleId}>
      <Heading id={titleId} className="empty-state__title">{title}</Heading>
      <p className="empty-state__description">{description}</p>
      {action && (
        <button type="button" className="empty-state__action" onClick={action.onClick}>
          {action.label}
        </button>
      )}
    </section>
  );
}

export default EmptyState;
