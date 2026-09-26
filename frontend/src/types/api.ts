export type ApiUser = {
  id: number;
  username: string;
  email: string;
  is_admin: boolean;
};

export type TestSession = {
  id: number;
  user_id: number;
  practice_test_id: string;
  start_time: string;
  score: number | null;
  current_question: number;
  current_section: number;
  section_start_time: string | null;
  is_complete: boolean;
};

export type SectionConfig = {
  name: string;
  type: "verbal" | "math";
  module: number;
  duration: number;
};

export type SatQuestion = {
  question_id?: number;
  type?: string;
  module?: number;
  question?: string;
  text?: string;
  passage?: string;
  options?: string[];
  correct_answer?: string | string[] | number;
  explanation?: string;
  image?: string;
  question_image?: string;
  equation?: string;
  domain?: string;
  skill?: string;
  level?: string;
  difficulty_label?: string;
};

export type TestState = {
  status: "in_progress" | "section_complete" | "test_complete";
  test_session: TestSession;
  sections?: SectionConfig[];
  section?: SectionConfig;
  section_idx?: number;
  question?: SatQuestion | null;
  qid?: number;
  answer?: string;
  marked?: boolean;
  answers?: Record<string, string>;
  marked_for_review?: Record<string, boolean>;
  total_questions?: number;
  section_name?: string;
  remaining_time?: number;
  next_section?: SectionConfig;
  next_route?: string;
};

export type DrillSet = {
  id: number;
  topic_name: string;
  skill_name: string;
  section_type: "verbal" | "math";
  set_number: number;
  difficulty: string;
  num_questions: number;
  question_ids: number[];
  description?: string;
};

export type DrillSession = {
  id: number;
  user_id: number;
  drill_set_id: number;
  start_time: string;
  end_time: string | null;
  duration_seconds: number | null;
  correct_count: number | null;
  total_count: number | null;
  accuracy_percent: number | null;
  use_timer: boolean;
  is_complete: boolean;
};

export type DrillState = {
  drill_session: DrillSession;
  drill_set: DrillSet;
  questions: SatQuestion[];
  answers: Record<string, string>;
  total_questions: number;
  status?: "in_progress" | "drill_complete";
  next_route?: string;
};

export type ReportPayload = {
  test_session: TestSession;
  practice_test_id: string;
  raw_score: number;
  verbal_score: number;
  math_score: number;
  total_score: number;
  section_reviews: Array<{
    section_idx: number;
    section: SectionConfig;
    score: number;
    total: number;
    questions: Array<{
      qid: number;
      question: SatQuestion;
      user_answer: string | null;
      marked: boolean;
      is_correct: boolean;
    }>;
  }>;
  domain_chart_data: Record<string, {
    labels: string[];
    correct: number[];
    incorrect: number[];
    totals: number[];
    pct_correct: number[];
    pct_incorrect: number[];
  }>;
  improvement_analysis: {
    priority_focus: Array<{ subject_label: string; domain: string; pct_correct: number }>;
    subject_analysis: Array<{
      subject: string;
      subject_label: string;
      correct: number;
      total: number;
      accuracy: number;
      recommendations: string[];
    }>;
  };
};
