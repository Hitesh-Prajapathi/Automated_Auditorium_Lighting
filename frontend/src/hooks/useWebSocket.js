
import { useState, useEffect, useRef, useCallback } from 'react';

const WS_BASE_URL = 'ws://localhost:8000/ws/progress';

export function useWebSocket(jobId) {
    const [status, setStatus] = useState('disconnected'); // 'connecting', 'connected', 'disconnected', 'error'
    const [messages, setMessages] = useState([]);
    const [latestMessage, setLatestMessage] = useState(null);
    const wsRef = useRef(null);
    const reconnectTimerRef = useRef(null);

    const connect = useCallback(() => {
        // Guard: don't open if no jobId, or if a connection already exists
        if (!jobId) return;
        if (wsRef.current && wsRef.current.readyState <= WebSocket.OPEN) return;

        setStatus('connecting');
        const ws = new WebSocket(`${WS_BASE_URL}/${jobId}`);
        wsRef.current = ws;

        ws.onopen = () => {
            console.log('✅ WebSocket Connected');
            setStatus('connected');
        };

        ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                setLatestMessage(data);
                setMessages((prev) => [...prev, data]);
            } catch (err) {
                console.error('Failed to parse WS message:', err);
            }
        };

        ws.onerror = (error) => {
            console.error('WebSocket Error:', error);
            setStatus('error');
        };

        ws.onclose = (event) => {
            console.log('WebSocket Disconnected', event.code);
            setStatus('disconnected');
            wsRef.current = null;

            // Auto-reconnect once if the close was abnormal (not user-initiated)
            // Code 1000 = normal close, 1005 = no status (React StrictMode cleanup)
            if (jobId && event.code !== 1000) {
                reconnectTimerRef.current = setTimeout(() => {
                    console.log('🔄 WebSocket auto-reconnecting...');
                    connect();
                }, 500);
            }
        };

        return ws;
    }, [jobId]);

    const disconnect = useCallback(() => {
        // Clear any pending reconnect
        if (reconnectTimerRef.current) {
            clearTimeout(reconnectTimerRef.current);
            reconnectTimerRef.current = null;
        }
        if (wsRef.current) {
            wsRef.current.close(1000, 'User disconnect');
            wsRef.current = null;
        }
    }, []);

    // Auto-connect when jobId changes; small delay to handle React StrictMode
    useEffect(() => {
        if (!jobId) return;

        // Small delay lets React StrictMode's first cleanup run before we connect
        const timer = setTimeout(() => {
            connect();
        }, 100);

        return () => {
            clearTimeout(timer);
            disconnect();
        };
    }, [jobId, connect, disconnect]);

    return { status, messages, latestMessage, connect, disconnect };
}
