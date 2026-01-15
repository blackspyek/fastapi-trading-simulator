import { useEffect, useRef, useCallback, useState } from "react";

interface PriceUpdate {
  ticker: string;
  price: number;
}

interface ServerStatus {
  cpu: number;
  ram: number;
}

interface WebSocketMessage {
  type: string;
  data?: PriceUpdate[];
  cpu?: number;
  ram?: number;
}

interface UseWebSocketReturn {
  prices: Record<string, number>;
  isConnected: boolean;
  serverStatus: ServerStatus | null;
}

export function useWebSocket(): UseWebSocketReturn {
  const [prices, setPrices] = useState<Record<string, number>>({});
  const [isConnected, setIsConnected] = useState(false);
  const [serverStatus, setServerStatus] = useState<ServerStatus | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const isMountedRef = useRef(true);

  const connect = useCallback(() => {
    if (!isMountedRef.current) return;
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) return;

    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const wsUrl = `${protocol}//${window.location.host}/ws`;

    try {
      const ws = new WebSocket(wsUrl);

      ws.onopen = () => {
        if (!isMountedRef.current) {
          ws.close();
          return;
        }
        console.log("WebSocket connected");
        wsRef.current = ws;
        setIsConnected(true);
      };

      ws.onmessage = (event) => {
        if (!isMountedRef.current) return;
        
        try {
          const message: WebSocketMessage = JSON.parse(event.data);

          if (message.type === "market_update" && Array.isArray(message.data)) {
            setPrices((prev) => {
              const updated = { ...prev };
              for (const item of message.data!) {
                updated[item.ticker] = item.price;
              }
              return updated;
            });
          } else if (message.type === "server_status") {
            setServerStatus({
              cpu: message.cpu ?? 0,
              ram: message.ram ?? 0,
            });
          }
        } catch (err) {
          console.error("WebSocket message parse error:", err);
        }
      };

      ws.onclose = () => {
        console.log("WebSocket disconnected");
        if (wsRef.current === ws) {
          wsRef.current = null;
        }
        setIsConnected(false);
        setServerStatus(null);
        
        if (isMountedRef.current) {
          reconnectTimeoutRef.current = setTimeout(() => {
            connect();
          }, 3000);
        }
      };

      ws.onerror = (error) => {
        console.error("WebSocket error:", error);
      };
    } catch (err) {
      console.error("WebSocket connection error:", err);
    }
  }, []);

  useEffect(() => {
    isMountedRef.current = true;
    connect();

    return () => {
      isMountedRef.current = false;
      
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
        reconnectTimeoutRef.current = null;
      }
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
    };
  }, [connect]);

  return { prices, isConnected, serverStatus };
}
