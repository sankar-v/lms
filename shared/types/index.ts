export interface User {
  id: number;
  email: string;
  username: string;
  full_name?: string;
  role: string;
  is_active: boolean;
  created_at: string;
}

export interface Module {
  id: number;
  title: string;
  description?: string;
  category?: string;
  difficulty_level?: string;
  duration_minutes?: number;
  prerequisites?: string[];
  learning_outcomes?: string[];
  content_url?: string;
  is_published: boolean;
  created_at: string;
}

export interface Progress {
  id: number;
  user_id: number;
  module_id: number;
  status: 'not_started' | 'in_progress' | 'completed';
  progress_percentage: number;
  started_at?: string;
  completed_at?: string;
  time_spent_minutes: number;
  created_at: string;
}

export interface ChatMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
}

export interface ChatResponse {
  answer: string;
  sources: string[];
  confidence: number;
}

export interface Recommendation {
  module: Module;
  reason: string;
  priority: number;
}
