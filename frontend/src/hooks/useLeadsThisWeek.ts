import { useQuery } from '@tanstack/react-query';

interface LeadsThisWeek {
  value: number;
  delta_pct: number;
  sparkline: number[];
}

export function useLeadsThisWeek() {
  return useQuery<LeadsThisWeek>({
    queryKey: ['leadsThisWeek'],
    queryFn: async () => {
      const { getAuthHeader } = await import('@/lib/api-client');
      const response = await fetch('/api/v1/activity/metric/leads_this_week', {
        headers: { Authorization: await getAuthHeader() },
      });
      if (!response.ok) throw new Error('Failed to fetch leads metric');
      return response.json();
    },
    staleTime: 5 * 60 * 1000,
  });
}
