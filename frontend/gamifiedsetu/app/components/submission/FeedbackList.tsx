type FeedbackListProps = {
  items: string[];
};

export default function FeedbackList({ items }: FeedbackListProps) {
  if (items.length === 0) {
    return null;
  }

  return (
    <ul className="list-disc space-y-1 pl-6 text-ink">
      {items.map((item, index) => (
        <li key={index}>{item}</li>
      ))}
    </ul>
  );
}