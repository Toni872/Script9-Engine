import { useQuery } from '@tanstack/react-query';

interface ActivityEvent {
  id: number;
  tipo: string;
  payload: Record<string, unknown>;
  creado_en: string;
}

interface ActivityFeed {
  total: number;
  days: number;
  events: ActivityEvent[];
}

export function useActivityFeed(days = 7) {
  return useQuery<ActivityFeed>({
    queryKey: ['activityFeed', days],
    queryFn: async () => {
      const { getAuthHeader } = await import('@/lib/api-client');
      const response = await fetch(`/api/v1/activity/feed?days=${days}`, {
        headers: { Authorization: await getAuthHeader() },
      });
      if (!response.ok) throw new Error('Failed to fetch activity feed');
      return response.json();
    },
    staleTime: 2 * 60 * 1000,
  });
}
