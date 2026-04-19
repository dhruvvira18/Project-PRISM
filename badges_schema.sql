-- badges_schema.sql
-- Schema additions for the gamification badge system

CREATE TABLE public.badges (
  id uuid NOT NULL DEFAULT uuid_generate_v4(),
  name character varying NOT NULL,
  description text NOT NULL,
  condition_type character varying NOT NULL, -- e.g., 'topics_learned', 'quiz_correct', 'session_minutes'
  condition_value integer NOT NULL,          -- e.g., 5, 5, 15
  icon_name character varying,
  points_reward integer DEFAULT 0,
  CONSTRAINT badges_pkey PRIMARY KEY (id)
);

CREATE TABLE public.user_badges (
  id uuid NOT NULL DEFAULT uuid_generate_v4(),
  user_id uuid NOT NULL,
  badge_id uuid NOT NULL,
  earned_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT user_badges_pkey PRIMARY KEY (id),
  CONSTRAINT user_badges_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id),
  CONSTRAINT user_badges_badge_id_fkey FOREIGN KEY (badge_id) REFERENCES public.badges(id)
);

-- Example Insert Data:
-- INSERT INTO public.badges (name, description, condition_type, condition_value) VALUES
-- ('Knowledge Seeker', 'Learned 5 topics', 'topics_learned', 5),
-- ('Quiz Starter', 'Answered 5 quizzes correctly', 'quiz_correct', 5),
-- ('Focus Starter', 'Studied for 15 minutes', 'session_minutes', 15);
