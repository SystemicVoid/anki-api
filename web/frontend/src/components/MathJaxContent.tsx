import { MathJax } from 'better-react-mathjax';

interface Props {
  text: string;
}

function processTextWithMath(text: string): React.ReactNode[] {
  const result: React.ReactNode[] = [];
  let remaining = text;
  let key = 0;

  const mathPatterns = [
    { open: '\\[', close: '\\]', display: true },
    { open: '\\(', close: '\\)', display: false },
  ];

  while (remaining.length > 0) {
    let earliestMatch: { index: number; pattern: (typeof mathPatterns)[0]; end: number } | null =
      null;

    for (const pattern of mathPatterns) {
      const openIndex = remaining.indexOf(pattern.open);
      if (openIndex === -1) continue;

      const closeIndex = remaining.indexOf(pattern.close, openIndex + pattern.open.length);
      if (closeIndex === -1) continue;

      if (!earliestMatch || openIndex < earliestMatch.index) {
        earliestMatch = {
          index: openIndex,
          pattern,
          end: closeIndex + pattern.close.length,
        };
      }
    }

    if (!earliestMatch) {
      result.push(...renderTextSegment(remaining, key));
      break;
    }

    if (earliestMatch.index > 0) {
      const textBefore = remaining.slice(0, earliestMatch.index);
      result.push(...renderTextSegment(textBefore, key));
      key += textBefore.split('\n').length;
    }

    const mathContent = remaining.slice(earliestMatch.index, earliestMatch.end);
    const normalizedMath = mathContent.replace(/\n/g, ' ');
    result.push(
      <MathJax key={`math-${key++}`} inline={!earliestMatch.pattern.display} dynamic>
        {normalizedMath}
      </MathJax>
    );

    remaining = remaining.slice(earliestMatch.end);
  }

  return result;
}

function renderTextSegment(text: string, startKey: number): React.ReactNode[] {
  const lines = text.split('\n');
  return lines.map((line, i) => (
    <span key={`text-${startKey + i}`}>
      {line}
      {i < lines.length - 1 && <br />}
    </span>
  ));
}

export function MathJaxContent({ text }: Props) {
  return <>{processTextWithMath(text)}</>;
}
