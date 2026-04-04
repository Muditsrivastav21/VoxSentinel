/**
 * React Query hooks for VoxSentinel API
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api, queryKeys, AnalysisResult, CallHistoryResponse, DashboardStats, ApiError } from '../lib/api';
import { useToast } from './use-toast';

// ==========================
// ANALYSIS HOOKS
// ==========================

export function useAnalyzeCall() {
  const { toast } = useToast();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ file, language }: { file: File; language: string }) => {
      return api.analyzeCallFromFile(file, language);
    },
    onSuccess: () => {
      // Invalidate history and stats after successful analysis
      queryClient.invalidateQueries({ queryKey: ['history'] });
      queryClient.invalidateQueries({ queryKey: queryKeys.stats });
      
      toast({
        title: 'Analysis Complete',
        description: 'Call has been analyzed successfully.',
      });
    },
    onError: (error: ApiError) => {
      toast({
        title: 'Analysis Failed',
        description: error.message || 'Failed to analyze call. Please try again.',
        variant: 'destructive',
      });
    },
  });
}

// ==========================
// HISTORY HOOKS
// ==========================

export function useCallHistory(page: number = 1, perPage: number = 20) {
  return useQuery<CallHistoryResponse, ApiError>({
    queryKey: queryKeys.history(page, perPage),
    queryFn: () => api.getCallHistory(page, perPage),
    staleTime: 30_000, // 30 seconds
    refetchOnWindowFocus: true,
  });
}

export function useCallById(id: string) {
  return useQuery({
    queryKey: queryKeys.call(id),
    queryFn: () => api.getCallById(id),
    enabled: !!id,
    staleTime: 60_000, // 1 minute
  });
}

export function useDeleteCall() {
  const { toast } = useToast();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => api.deleteCall(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['history'] });
      queryClient.invalidateQueries({ queryKey: queryKeys.stats });
      
      toast({
        title: 'Call Deleted',
        description: 'Call record has been removed.',
      });
    },
    onError: (error: ApiError) => {
      toast({
        title: 'Delete Failed',
        description: error.message || 'Failed to delete call.',
        variant: 'destructive',
      });
    },
  });
}

// ==========================
// STATS HOOKS
// ==========================

export function useDashboardStats() {
  return useQuery<DashboardStats, ApiError>({
    queryKey: queryKeys.stats,
    queryFn: () => api.getDashboardStats(),
    staleTime: 30_000, // 30 seconds
    refetchInterval: 60_000, // Auto-refresh every 1 minute
    refetchOnWindowFocus: true,
  });
}

// ==========================
// HEALTH HOOKS
// ==========================

export function useHealthCheck() {
  return useQuery({
    queryKey: queryKeys.health,
    queryFn: () => api.getHealth(),
    staleTime: 60_000,
    retry: 1,
  });
}
