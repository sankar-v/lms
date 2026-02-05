-- Insert sample users
INSERT INTO users (email, username, hashed_password, full_name, role) VALUES
('john.doe@example.com', 'johndoe', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyK5U9gJf8pO', 'John Doe', 'platform_engineer'),
('jane.smith@example.com', 'janesmith', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyK5U9gJf8pO', 'Jane Smith', 'backend_engineer'),
('bob.wilson@example.com', 'bobwilson', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyK5U9gJf8pO', 'Bob Wilson', 'frontend_engineer');

-- Insert sample modules
INSERT INTO modules (title, description, category, difficulty_level, duration_minutes, prerequisites, learning_outcomes, is_published) VALUES
('Introduction to Platform Engineering', 'Learn the fundamentals of platform engineering and DevOps practices', 'Platform', 'Beginner', 120, '[]'::jsonb, '["Understand platform concepts", "Learn CI/CD basics"]'::jsonb, TRUE),
('Kubernetes Fundamentals', 'Master container orchestration with Kubernetes', 'Platform', 'Intermediate', 180, '["Introduction to Platform Engineering"]'::jsonb, '["Deploy containers", "Manage pods and services"]'::jsonb, TRUE),
('Advanced Kubernetes Patterns', 'Deep dive into advanced Kubernetes patterns and best practices', 'Platform', 'Advanced', 240, '["Kubernetes Fundamentals"]'::jsonb, '["Implement operators", "Design scalable architectures"]'::jsonb, TRUE),
('API Design Best Practices', 'Learn how to design robust and scalable APIs', 'Backend', 'Intermediate', 150, '[]'::jsonb, '["Design RESTful APIs", "Implement API versioning"]'::jsonb, TRUE),
('Microservices Architecture', 'Understanding microservices patterns and implementation', 'Backend', 'Advanced', 200, '["API Design Best Practices"]'::jsonb, '["Design microservices", "Implement service mesh"]'::jsonb, TRUE),
('React Advanced Patterns', 'Master advanced React patterns and hooks', 'Frontend', 'Advanced', 180, '[]'::jsonb, '["Use custom hooks", "Optimize performance"]'::jsonb, TRUE);

-- Insert sample user skills
INSERT INTO user_skills (user_id, skill_name, proficiency_level) VALUES
(1, 'Docker', 'Intermediate'),
(1, 'Python', 'Advanced'),
(2, 'Java', 'Advanced'),
(2, 'Spring Boot', 'Intermediate'),
(3, 'React', 'Advanced'),
(3, 'TypeScript', 'Intermediate');

-- Insert sample progress
INSERT INTO progress (user_id, module_id, status, progress_percentage, started_at) VALUES
(1, 1, 'completed', 100, NOW() - INTERVAL '7 days'),
(1, 2, 'in_progress', 45, NOW() - INTERVAL '2 days'),
(2, 4, 'in_progress', 30, NOW() - INTERVAL '1 day'),
(3, 6, 'completed', 100, NOW() - INTERVAL '5 days');

-- Insert sample quizzes
INSERT INTO quizzes (module_id, title, description, passing_score, time_limit_minutes) VALUES
(1, 'Platform Engineering Basics Quiz', 'Test your knowledge of platform engineering fundamentals', 70.0, 30),
(2, 'Kubernetes Knowledge Check', 'Assess your understanding of Kubernetes concepts', 75.0, 45);

-- Insert sample quiz questions
INSERT INTO quiz_questions (quiz_id, question_text, question_type, options, correct_answer, points) VALUES
(1, 'What does CI/CD stand for?', 'multiple_choice', 
 '["Continuous Integration/Continuous Deployment", "Computer Integration/Computer Deployment", "Code Integration/Code Development", "Continuous Improvement/Continuous Development"]'::jsonb,
 '"Continuous Integration/Continuous Deployment"'::jsonb, 1),
(1, 'Which of the following are benefits of platform engineering?', 'multiple_select',
 '["Faster deployment", "Reduced costs", "Better security", "All of the above"]'::jsonb,
 '["All of the above"]'::jsonb, 2);

-- Insert sample learning paths
INSERT INTO learning_paths (user_id, module_id, sequence_order, is_recommended) VALUES
(1, 1, 1, TRUE),
(1, 2, 2, TRUE),
(1, 3, 3, TRUE),
(2, 4, 1, TRUE),
(2, 5, 2, TRUE),
(3, 6, 1, TRUE);
