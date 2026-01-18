import { useEffect, useRef, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import type { GenerationMessage } from '../types';
import styles from './CardGeneration.module.css';

const WS_URL = 'ws://localhost:8080/api/ws/generate';

export function CardGeneration() {
  const [messages, setMessages] = useState<GenerationMessage[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isComplete, setIsComplete] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const messagesEndRef = useRef<HTMLDivElement | null>(null);
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  const source = searchParams.get('source');
  const tags = searchParams.get('tags');

  useEffect(() => {
    if (!source) {
      setError('No source provided');
      return;
    }

    // Connect to WebSocket
    const ws = new WebSocket(WS_URL);
    wsRef.current = ws;

    ws.onopen = () => {
      setIsConnected(true);
      // Send initial request
      ws.send(
        JSON.stringify({
          source,
          tags: tags || '',
        })
      );
    };

    ws.onmessage = (event) => {
      try {
        const message: GenerationMessage = JSON.parse(event.data);
        setMessages((prev) => [...prev, message]);

        // Handle completion
        if (message.type === 'complete' && message.data.filename) {
          setIsComplete(true);
          // Auto-redirect after 2 seconds
          setTimeout(() => {
            navigate(`/review?file=${encodeURIComponent(message.data.filename!)}`);
          }, 2000);
        }

        // Handle errors
        if (message.type === 'error') {
          setError(message.data.message || 'Unknown error occurred');
        }
      } catch (err) {
        console.error('Failed to parse WebSocket message:', err);
      }
    };

    ws.onerror = (event) => {
      console.error('WebSocket error:', event);
      setError('Connection error. Please ensure the backend is running.');
      setIsConnected(false);
    };

    ws.onclose = () => {
      setIsConnected(false);
    };

    // Cleanup on unmount
    return () => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.close();
      }
    };
  }, [source, tags, navigate]);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  const renderMessage = (message: GenerationMessage, index: number) => {
    const { type, data } = message;

    switch (type) {
      case 'status':
        return (
          <div key={index} className={`${styles.message} ${styles.messageStatus}`}>
            <span className={styles.messageIcon}>ℹ</span>
            <div className={styles.messageContent}>
              <p>{data.message}</p>
            </div>
          </div>
        );

      case 'text':
        return (
          <div key={index} className={`${styles.message} ${styles.messageText}`}>
            <span className={styles.messageIcon}>💭</span>
            <div className={styles.messageContent}>
              <p>{data.content}</p>
            </div>
          </div>
        );

      case 'tool':
        return (
          <div key={index} className={`${styles.message} ${styles.messageTool}`}>
            <span className={styles.messageIcon}>🔧</span>
            <div className={styles.messageContent}>
              <p className={styles.toolName}>{data.name}</p>
              {data.input && (
                <pre className={styles.toolInput}>{JSON.stringify(data.input, null, 2)}</pre>
              )}
            </div>
          </div>
        );

      case 'complete':
        return (
          <div key={index} className={`${styles.message} ${styles.messageComplete}`}>
            <span className={styles.messageIcon}>✓</span>
            <div className={styles.messageContent}>
              <p>{data.message}</p>
              <p className={styles.redirectMessage}>Redirecting to review...</p>
            </div>
          </div>
        );

      case 'error':
        return (
          <div key={index} className={`${styles.message} ${styles.messageError}`}>
            <span className={styles.messageIcon}>✗</span>
            <div className={styles.messageContent}>
              <p>{data.message}</p>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  if (!source) {
    return (
      <div className={styles.container}>
        <div className={styles.error}>
          <h2>Missing Source</h2>
          <p>No source URL or file path provided.</p>
          <button type="button" onClick={() => navigate('/review')} className={styles.backButton}>
            Back to Home
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      <div className={styles.content}>
        <header className={styles.header}>
          <h1 className={styles.title}>Generating Flashcards</h1>
          <p className={styles.subtitle}>
            {source.startsWith('http') ? 'From URL' : 'From File'}: {source}
          </p>
          {tags && <p className={styles.tags}>Tags: {tags}</p>}
        </header>

        <div className={styles.messagesContainer}>
          {!isConnected && !error && (
            <div className={styles.connecting}>
              <div className={styles.spinner} />
              <p>Connecting...</p>
            </div>
          )}

          {messages.map((message, index) => renderMessage(message, index))}

          {error && !isComplete && (
            <div className={styles.errorFooter}>
              <button
                type="button"
                onClick={() => navigate('/review')}
                className={styles.backButton}
              >
                Back to Home
              </button>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </div>
    </div>
  );
}
