export const API_ENDPOINTS = {
  USERS: '/users',
  MODULES: '/modules',
  PROGRESS: '/progress',
  RECOMMENDATIONS: '/recommendations',
  CHAT: '/chat',
} as const;

export const USER_ROLES = {
  PLATFORM_ENGINEER: 'platform_engineer',
  BACKEND_ENGINEER: 'backend_engineer',
  FRONTEND_ENGINEER: 'frontend_engineer',
  DEVOPS_ENGINEER: 'devops_engineer',
} as const;

export const MODULE_CATEGORIES = {
  PLATFORM: 'Platform',
  BACKEND: 'Backend',
  FRONTEND: 'Frontend',
  DEVOPS: 'DevOps',
  SECURITY: 'Security',
  TESTING: 'Testing',
} as const;

export const DIFFICULTY_LEVELS = {
  BEGINNER: 'Beginner',
  INTERMEDIATE: 'Intermediate',
  ADVANCED: 'Advanced',
} as const;

export const PROGRESS_STATUS = {
  NOT_STARTED: 'not_started',
  IN_PROGRESS: 'in_progress',
  COMPLETED: 'completed',
} as const;
