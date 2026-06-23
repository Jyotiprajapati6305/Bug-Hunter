import { useEffect, useState } from "react";
import { useAuth } from "@/hooks/useAuth";
import { xpService } from "@/services/xpService";
import { Card } from "@/components/ui/Card";
import { ProgressBar } from "@/components/ui/ProgressBar";
import { Badge } from "@/components/ui/Badge";
import type { LevelInfo, XpTransaction } from "@/services/types";

function StatCard({ label, value }: { label: string; value: number | string }) {
  return (
    <Card className="flex flex-col gap-1">
      <span className="text-sm text-muted">{label}</span>
      <span className="text-3xl font-bold">{value}</span>
    </Card>
  );
}

export function DashboardPage() {
  const { user, refreshUser } = useAuth();
  const [transactions, setTransactions] = useState<XpTransaction[]>([]);
  const [levels, setLevels] = useState<LevelInfo[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;
    async function load() {
      try {
        await refreshUser();
        const [tx, lvls] = await Promise.all([xpService.myTransactions(), xpService.levels()]);
        if (mounted) {
          setTransactions(tx);
          setLevels(lvls);
        }
      } finally {
        if (mounted) setLoading(false);
      }
    }
    load();
    return () => {
      mounted = false;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  if (loading || !user) {
    return <div className="text-muted">Loading dashboard...</div>;
  }

  const currentLevelInfo = levels.find((l) => l.level === user.profile.level);
  const nextLevelInfo = levels.find((l) => l.level === user.profile.level + 1);
  const currentFloor = currentLevelInfo?.xp_required ?? 0;
  const nextCeiling = nextLevelInfo?.xp_required ?? currentFloor + 100;
  const xpIntoLevel = user.profile.xp_total - currentFloor;
  const xpNeededForLevel = nextCeiling - currentFloor;

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold">Welcome back, {user.profile.display_name ?? user.username}</h1>
        <p className="text-sm text-muted">Here's how your bug-hunting journey is going.</p>
      </div>

      <Card>
        <div className="flex items-center justify-between">
          <div>
            <span className="text-sm text-muted">Current level</span>
            <div className="flex items-baseline gap-2">
              <span className="text-4xl font-bold">{user.profile.level}</span>
              <Badge>{user.profile.xp_total} XP total</Badge>
            </div>
          </div>
          <Badge className="text-base">Rank: Unranked (coming soon)</Badge>
        </div>
        <div className="mt-4">
          <div className="mb-1 flex justify-between text-xs text-muted">
            <span>{xpIntoLevel} XP</span>
            <span>
              {xpNeededForLevel} XP to level {user.profile.level + 1}
            </span>
          </div>
          <ProgressBar value={xpIntoLevel} max={xpNeededForLevel} />
        </div>
      </Card>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <StatCard label="Bugs found" value={user.profile.bugs_found_count} />
        <StatCard label="Challenges completed" value={user.profile.challenges_completed_count} />
        <StatCard label="Test cases written" value={user.profile.test_cases_written_count} />
      </div>

      <Card>
        <h2 className="mb-4 text-lg font-semibold">Recent activity</h2>
        {transactions.length === 0 ? (
          <p className="text-sm text-muted">No XP transactions yet — go find some bugs!</p>
        ) : (
          <ul className="divide-y divide-border">
            {transactions.map((tx) => (
              <li key={tx.id} className="flex items-center justify-between py-3 text-sm">
                <div>
                  <p className="font-medium">{tx.reason}</p>
                  <p className="text-xs text-muted">{new Date(tx.created_at).toLocaleString()}</p>
                </div>
                <span className={tx.amount >= 0 ? "font-semibold text-foreground" : "font-semibold text-red-400"}>
                  {tx.amount >= 0 ? "+" : ""}
                  {tx.amount} XP
                </span>
              </li>
            ))}
          </ul>
        )}
      </Card>
    </div>
  );
}
