'use client';

import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism';
import React from 'react';

interface MarkdownRendererProps {
  content: string;
  className?: string;
}

export default function MarkdownRenderer({ content, className = '' }: MarkdownRendererProps) {
  return (
    <div className={`md-rendered ${className}`}>
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          code({ node, className: codeClassName, children, ...props }) {
            const match = /language-(\w+)/.exec(codeClassName || '');
            const isInline = !match && !String(children).includes('\n');
            
            if (isInline) {
              return (
                <code className="md-inline-code" {...props}>
                  {children}
                </code>
              );
            }
            
            return (
              <div className="md-code-block">
                {match && (
                  <div className="md-code-lang">{match[1]}</div>
                )}
                <SyntaxHighlighter
                  style={oneDark as Record<string, React.CSSProperties>}
                  language={match?.[1] || 'text'}
                  PreTag="div"
                  customStyle={{
                    margin: 0,
                    borderRadius: '0 0 8px 8px',
                    fontSize: '0.85rem',
                    lineHeight: '1.5',
                  }}
                >
                  {String(children).replace(/\n$/, '')}
                </SyntaxHighlighter>
              </div>
            );
          },
          h1({ children }) {
            return <h1 className="md-h1">{children}</h1>;
          },
          h2({ children }) {
            return <h2 className="md-h2">{children}</h2>;
          },
          h3({ children }) {
            return <h3 className="md-h3">{children}</h3>;
          },
          p({ children }) {
            return <p className="md-p">{children}</p>;
          },
          ul({ children }) {
            return <ul className="md-ul">{children}</ul>;
          },
          ol({ children }) {
            return <ol className="md-ol">{children}</ol>;
          },
          li({ children }) {
            return <li className="md-li">{children}</li>;
          },
          strong({ children }) {
            return <strong className="md-strong">{children}</strong>;
          },
          blockquote({ children }) {
            return <blockquote className="md-blockquote">{children}</blockquote>;
          },
          hr() {
            return <hr className="md-hr" />;
          },
          table({ children }) {
            return (
              <div className="md-table-wrapper">
                <table className="md-table">{children}</table>
              </div>
            );
          },
          th({ children }) {
            return <th className="md-th">{children}</th>;
          },
          td({ children }) {
            return <td className="md-td">{children}</td>;
          },
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
}
