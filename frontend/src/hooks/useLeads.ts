import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

interface Lead {
  id: number;
  email: string;
  nombre: string;
  empresa: string;
  score: number;
  estado: string;
  creado_en: string;
}

interface LeadCreate {
  slug: string;
  email: string;
  nombre: string;
  empresa: string;
  mensaje: string;
  telefono?: string;
}

export function useLeads() {
  return useQuery<Lead[]>({
    queryKey: ['leads'],
    queryFn: async () => {
      const { getAuthHeader } = await import('@/lib/api-client');
      const response = await fetch('/api/v1/leads', {
        headers: { Authorization: await getAuthHeader() },
      });
      if (!response.ok) throw new Error('Failed to fetch leads');
      return response.json();
    },
  });
}

export function useCreateLead() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (data: LeadCreate) => {
      const response = await fetch('/api/v1/leads', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });
      if (!response.ok) throw new Error('Failed to create lead');
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['leads'] });
      queryClient.invalidateQueries({ queryKey: ['leadsThisWeek'] });
      queryClient.invalidateQueries({ queryKey: ['activityFeed'] });
    },
  });
}
