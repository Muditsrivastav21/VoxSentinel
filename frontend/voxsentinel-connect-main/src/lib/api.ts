/**
 * VoxSentinel API Client
 * 
 * Handles all communication with the backend API
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const API_KEY = import.meta.env.VITE_API_KEY || 'sk_track3_987654321';

// ==========================
// TYPES
// ==========================

export interface SOPValidation {
  greeting: boolean;
  identification: boolean;
  problemStatement: boolean;
  solutionOffering: boolean;
  closing: boolean;
  complianceScore: number;
  adherenceStatus: 'Compliant' | 'Non-Compliant' | 'Partial';
  explanation: string;
}

export interface Analytics {
  paymentPreference: string;
  rejectionReason: string;
  sentiment: 'Positive' | 'Neutral' | 'Negative';
}

export interface AnalysisResult {
  status: string;
  id: string;
  language: string;
  transcript: string;
  summary: string;
  sop_validation: SOPValidation;
  analytics: Analytics;
  keywords: string[];
  timestamp: string;
}

export interface CallHistoryItem {
  id: string;
  language: string;
  compliance_score: number;
  adherence_status: string;
  sentiment: string;
  created_at: string;
  summary?: string;
  payment_preference?: string;
}

export interface CallHistoryResponse {
  status: string;
  total: number;
  page: number;
  per_page: number;
  calls: CallHistoryItem[];
}

export interface DashboardStats {
  status: string;
  total_calls: number;
  avg_compliance: number;
  compliant_calls: number;
  non_compliant_calls: number;
  partial_calls: number;
  sentiment_distribution: {
    positive: number;
    neutral: number;
    negative: number;
  };
  recent_calls: CallHistoryItem[];
  calls_today: number;
  calls_this_week: number;
}

export interface HealthStatus {
  status: string;
  service: string;
  version: string;
  openai_configured: boolean;
  database_configured: boolean;
  environment: string;
  timestamp: string;
}

// ==========================
// API CLIENT
// ==========================

class ApiClient {
  private baseUrl: string;
  private apiKey: string;

  constructor() {
    this.baseUrl = API_BASE_URL;
    this.apiKey = API_KEY;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      'X-API-Key': this.apiKey,
      ...options.headers,
    };

    const response = await fetch(url, {
      ...options,
      headers,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      
      // Handle Pydantic validation errors (array of objects) and string errors
      let errorMessage = `Request failed: ${response.statusText}`;
      if (typeof errorData.detail === 'string') {
        errorMessage = errorData.detail;
      } else if (Array.isArray(errorData.detail)) {
        // Pydantic validation error - extract meaningful messages
        errorMessage = errorData.detail
          .map((err: { msg?: string; loc?: string[] }) => {
            const field = err.loc?.slice(-1)[0] || 'field';
            return err.msg || `Invalid ${field}`;
          })
          .join(', ');
      }
      
      throw new ApiError(
        errorMessage,
        response.status,
        errorData
      );
    }

    return response.json();
  }

  // ==========================
  // HEALTH ENDPOINTS
  // ==========================

  async getHealth(): Promise<HealthStatus> {
    return this.request<HealthStatus>('/health');
  }

  async ping(): Promise<{ status: string }> {
    return this.request('/ping');
  }

  // ==========================
  // ANALYSIS ENDPOINTS
  // ==========================

  async analyzeCall(audioBase64: string, language: string = 'en'): Promise<AnalysisResult> {
    return this.request<AnalysisResult>('/api/call-analytics', {
      method: 'POST',
      body: JSON.stringify({
        audio_base64: audioBase64,
        language,
      }),
    });
  }

  async analyzeCallFromFile(file: File, language: string = 'en'): Promise<AnalysisResult> {
    // Convert file to base64
    const base64 = await this.fileToBase64(file);
    return this.analyzeCall(base64, language);
  }

  private fileToBase64(file: File): Promise<string> {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.readAsDataURL(file);
      reader.onload = () => {
        const result = reader.result as string;
        // Remove the data URL prefix (e.g., "data:audio/wav;base64,")
        const base64 = result.split(',')[1];
        resolve(base64);
      };
      reader.onerror = (error) => reject(error);
    });
  }

  // ==========================
  // HISTORY ENDPOINTS
  // ==========================

  async getCallHistory(
    page: number = 1,
    perPage: number = 20
  ): Promise<CallHistoryResponse> {
    return this.request<CallHistoryResponse>(
      `/api/history?page=${page}&per_page=${perPage}`
    );
  }

  async getCallById(id: string): Promise<{ status: string; call: CallHistoryItem }> {
    return this.request(`/api/history/${id}`);
  }

  async deleteCall(id: string): Promise<{ status: string; message: string }> {
    return this.request(`/api/history/${id}`, {
      method: 'DELETE',
    });
  }

  // ==========================
  // STATS ENDPOINTS
  // ==========================

  async getDashboardStats(): Promise<DashboardStats> {
    return this.request<DashboardStats>('/api/stats');
  }
}

// ==========================
// ERROR HANDLING
// ==========================

export class ApiError extends Error {
  status: number;
  data: unknown;

  constructor(message: string, status: number, data?: unknown) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.data = data;
  }
}

// ==========================
// SINGLETON EXPORT
// ==========================

export const api = new ApiClient();

// ==========================
// REACT QUERY HELPERS
// ==========================

export const queryKeys = {
  health: ['health'] as const,
  history: (page: number, perPage: number) => ['history', page, perPage] as const,
  call: (id: string) => ['call', id] as const,
  stats: ['stats'] as const,
};
