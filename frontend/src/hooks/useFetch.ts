import { useCallback, useEffect, useRef, useState } from "react";
import { ApiError } from "@/lib/api";

export function useFetch<T>(
  fetcher: () => Promise<T>,
  deps: unknown[] = []
) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const fetcherRef = useRef(fetcher);
  const depsKey = JSON.stringify(deps);

  useEffect(() => {
    fetcherRef.current = fetcher;
  });

  const load = useCallback(() => {
    let active = true;
    setLoading(true);
    setError(null);
    fetcherRef.current()
      .then((result) => {
        if (active) setData(result);
      })
      .catch((err) => {
        if (active) {
          setError(err instanceof ApiError ? err.message : "Something went wrong.");
        }
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, []);

  useEffect(() => {
    let cleanup: (() => void) | undefined;
    const timeout = window.setTimeout(() => {
      cleanup = load();
    }, 0);

    return () => {
      window.clearTimeout(timeout);
      cleanup?.();
    };
  }, [depsKey, load]);

  return { data, loading, error, reload: load };
}
