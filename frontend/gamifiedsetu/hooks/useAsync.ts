"use client";

import { useCallback, useEffect, useState } from "react";

type UseAsyncState<T> = {
  data: T | null;
  loading: boolean;
  error: string | null;
  reload: () => void;
};

export function useAsync<T>(
  asyncFunction: () => Promise<T>
): UseAsyncState<T> {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [reloadKey, setReloadKey] = useState(0);

    const reload = useCallback(() => {
    setLoading(true);
    setError(null);
    setReloadKey((currentKey) => currentKey + 1);
  }, []);
    useEffect(() => {
    let ignore = false;

    asyncFunction()
      .then((result) => {
        if (!ignore) {
          setData(result);
          setError(null);
        }
      })
      .catch((err: unknown) => {
        if (!ignore) {
          setError(
            err instanceof Error
              ? err.message
              : "Something went wrong"
          );
        }
      })
      .finally(() => {
        if (!ignore) {
          setLoading(false);
        }
      });

    return () => {
      ignore = true;
    };
  }, [asyncFunction, reloadKey]);
    return {
    data,
    loading,
    error,
    reload,
  };
}