import type { CSSProperties, ReactNode } from "react";
import "../../styles/skeleton.css";

export type SkeletonVariant = "line" | "block" | "circle" | "pill";

interface SkeletonProps {
  variant?: SkeletonVariant;
  width?: CSSProperties["width"];
  height?: CSSProperties["height"];
  className?: string;
}

export function Skeleton({
  variant = "line",
  width,
  height,
  className = "",
}: SkeletonProps) {
  const style: CSSProperties = {};
  if (width !== undefined) style.width = width;
  if (height !== undefined) style.height = height;

  return (
    <span
      className={
        "skeleton-shape skeleton-shape--" + variant +
        (className ? " " + className : "")
      }
      style={style}
      aria-hidden="true"
    />
  );
}

interface SkeletonStatusProps {
  label: string;
  children: ReactNode;
  className?: string;
  as?: "div" | "span";
}

export function SkeletonStatus({
  label,
  children,
  className = "",
  as = "div",
}: SkeletonStatusProps) {
  const Element = as;

  return (
    <Element
      className={"skeleton-status" + (className ? " " + className : "")}
      role="status"
      aria-live="polite"
      aria-busy="true"
    >
      <span className="skeleton-sr-only">{label}</span>
      {children}
    </Element>
  );
}
