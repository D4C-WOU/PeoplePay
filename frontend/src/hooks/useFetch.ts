import { useCallback, useEffect, useRef, useState } from "react";
import { ApiError } from "@/lib/api";

export function useFetch<T>(fetcher: () => Promise<T>, deps: unknown[] = []) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const fetcherRef = useRef(fetcher);
  const requestId = useRef(0);
  const depsKey = JSON.stringify(deps);

  useEffect(() => {
    fetcherRef.current = fetcher;
  });

  const load = useCallback(() => {
    const id = ++requestId.current;
    setLoading(true);
    setError(null);

    fetcherRef.current()
      .then((result) => {
        if (id === requestId.current) {
          setData(result);
        }
      })
      .catch((err) => {
        if (id === requestId.current) {
          setError(
            err instanceof ApiError
              ? err.message
              : "Something went wrong.",
          );
        }
      })
      .finally(() => {
        if (id === requestId.current) {
          setLoading(false);
        }
      });
  }, []);

  useEffect(() => {
    load();
  }, [depsKey, load]);

  return { data, loading, error, reload: load };
}