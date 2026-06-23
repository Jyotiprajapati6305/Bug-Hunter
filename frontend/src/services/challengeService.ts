import { apiClient } from "@/services/apiClient";
import type {
  BugSubmitPayload,
  BugSubmitResult,
  Challenge,
  ChallengeDetail,
  ChallengeSession,
} from "@/services/types";

export interface ChallengeFilters {
  category_id?: number;
  type?: string;
  difficulty?: string;
}

export const challengeService = {
  async list(filters: ChallengeFilters = {}) {
    const resp = await apiClient.get<Challenge[]>("/challenges", { params: filters });
    return resp.data;
  },

  async get(id: string) {
    const resp = await apiClient.get<ChallengeDetail>(`/challenges/${id}`);
    return resp.data;
  },

  async start(id: string) {
    const resp = await apiClient.post<ChallengeSession>(`/challenges/${id}/start`);
    return resp.data;
  },

  async submitBug(id: string, payload: BugSubmitPayload) {
    const resp = await apiClient.post<BugSubmitResult>(`/challenges/${id}/submit-bug`, payload);
    return resp.data;
  },
};
