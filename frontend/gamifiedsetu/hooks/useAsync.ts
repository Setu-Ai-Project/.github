"use client";

import { useCallback, useEffect, useState } from "react";

type UseAsyncState<T> = {
  data: T | null;
  loading: boolean;
  error: Error | null;
  reload: () => void;
};

// `asyncFunction` must be stable. Wrap it in useCallback with the ids it uses, e.g.
//   const load = useCallback(() => getQuiz(moduleId), [moduleId]);
// If you pass a new arrow function every render, the effect re-runs every
// render and loads forever.
export function useAsync<T>(
  asyncFunction: () => Promise<T>
): UseAsyncState<T> {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
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
          setError(err instanceof Error ? err : new Error(String(err)));
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