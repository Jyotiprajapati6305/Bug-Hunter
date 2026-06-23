export interface UserProfile {
  display_name: string | null;
  bio: string | null;
  avatar_url: string | null;
  xp_total: number;
  level: number;
  bugs_found_count: number;
  challenges_completed_count: number;
  test_cases_written_count: number;
}

export interface UserMe {
  id: string;
  email: string;
  username: string;
  role: "admin" | "developer" | "tester";
  is_active: boolean;
  is_verified: boolean;
  profile: UserProfile;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface Challenge {
  id: string;
  title: string;
  difficulty: "beginner" | "intermediate" | "advanced" | "expert";
  type: "functional" | "ui" | "api" | "security" | "performance";
  base_xp: number;
  category_id: number | null;
  is_published: boolean;
}

export interface ChallengeDetail extends Challenge {
  description: string;
  environment_url: string | null;
}

export interface ChallengeSession {
  id: string;
  challenge_id: string;
  user_id: string;
  status: "active" | "completed" | "abandoned";
  started_at: string;
  completed_at: string | null;
}

export interface BugSubmitPayload {
  title: string;
  description: string;
  steps_to_reproduce: string;
  actual_result: string;
  expected_result: string;
  severity: "critical" | "high" | "medium" | "low";
  priority: "urgent" | "high" | "normal" | "low";
  is_duplicate?: boolean;
}

export interface BugSubmitResult {
  id: string;
  title: string;
  severity: string;
  priority: string;
  status: string;
  xp_awarded: number;
  new_xp_total: number;
  new_level: number;
}

export interface XpTransaction {
  id: string;
  amount: number;
  reason: string;
  reference_type: string | null;
  reference_id: string | null;
  created_at: string;
}

export interface LevelInfo {
  level: number;
  xp_required: number;
}
