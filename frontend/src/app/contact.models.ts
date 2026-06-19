export interface ContactRequest {
  name: string;
  email: string;
  phone: string;
  comment: string;
}

export type EmailDeliveryStatus = 'sent' | 'queued';

export interface AIAnalysis {
  category: string;
  sentiment: string;
  summary: string;
  priority: 'low' | 'normal' | 'high' | string;
  confidence: number;
  fallback_used: boolean;
}

export interface ContactResponse {
  id: string;
  status: 'accepted';
  email_delivery: EmailDeliveryStatus;
  ai: AIAnalysis;
  created_at: string;
}

export interface ApiErrorResponse {
  error?: {
    code?: string;
    message?: string;
    details?: Record<string, unknown>;
  };
  detail?: unknown;
}
