import { apiClient } from "@/services/apiClient";
import type { LevelInfo, XpTransaction } from "@/services/types";

export const xpService = {
  async myTransactions() {
    const resp = await apiClient.get<XpTransaction[]>("/xp/me/transactions");
    return resp.data;
  },

  async levels() {
    const resp = await apiClient.get<{ levels: LevelInfo[] }>("/xp/levels");
    return resp.data.levels;
  },
};
