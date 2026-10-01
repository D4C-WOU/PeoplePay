import {
  useCallback,
  useEffect,
  useRef,
  useState,
} from "react";

import { ApiError } from "@/lib/api";

export function useFetch<T>(
  fetcher: () => Promise<T>,
  deps: unknown[] = [],
) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  /*
   * Keep the latest fetcher without making the fetch effect depend
   * on the function identity.
   *
   * This is useful because callers may create a new fetcher function
   * during a render even when the actual API dependencies have not
   * changed.
   */
  const fetcherRef = useRef(fetcher);

  /*
   * Every request gets an ID.
   *
   * If a newer request finishes before an older request, the older
   * response is ignored. This prevents stale API responses from
   * overwriting newer data.
   */
  const requestId = useRef(0);

  /*
   * Convert the dependency array into a stable value that can be
   * used by the effect to detect dependency changes.
   */
  const depsKey = JSON.stringify(deps);

  /*
   * Always keep the ref pointing at the newest fetcher.
   */
  useEffect(() => {
    fetcherRef.current = fetcher;
  });

  const load = useCallback(() => {
    const id = ++requestId.current;

    setLoading(true);
    setError(null);

    fetcherRef.current()
      .then((result) => {
        /*
         * Only the newest request is allowed to update the data.
         */
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
    /*
     * The effect is responsible for starting the external API
     * operation. Scheduling it as a task prevents the effect itself
     * from synchronously triggering React state updates.
     */
    const timer = window.setTimeout(() => {
      load();
    }, 0);

    return () => {
      window.clearTimeout(timer);
    };
  }, [depsKey, load]);

  return {
    data,
    loading,
    error,
    reload: load,
  };
}