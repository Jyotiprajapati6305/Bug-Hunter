import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { challengeService } from "@/services/challengeService";
import type { Challenge } from "@/services/types";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";

const TYPES = ["functional", "ui", "api", "security", "performance"];
const DIFFICULTIES = ["beginner", "intermediate", "advanced", "expert"];

export function ChallengesListPage() {
  const [challenges, setChallenges] = useState<Challenge[]>([]);
  const [type, setType] = useState<string>("");
  const [difficulty, setDifficulty] = useState<string>("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;
    setLoading(true);
    challengeService
      .list({ type: type || undefined, difficulty: difficulty || undefined })
      .then((data) => {
        if (mounted) setChallenges(data);
      })
      .finally(() => {
        if (mounted) setLoading(false);
      });
    return () => {
      mounted = false;
    };
  }, [type, difficulty]);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Challenges</h1>
        <p className="text-sm text-muted">Pick a challenge and start hunting for bugs.</p>
      </div>

      <div className="flex flex-wrap gap-3">
        <select
          value={type}
          onChange={(e) => setType(e.target.value)}
          className="input-field w-auto"
        >
          <option value="">All types</option>
          {TYPES.map((t) => (
            <option key={t} value={t}>
              {t}
            </option>
          ))}
        </select>
        <select
          value={difficulty}
          onChange={(e) => setDifficulty(e.target.value)}
          className="input-field w-auto"
        >
          <option value="">All difficulties</option>
          {DIFFICULTIES.map((d) => (
            <option key={d} value={d}>
              {d}
            </option>
          ))}
        </select>
      </div>

      {loading ? (
        <p className="text-muted">Loading challenges...</p>
      ) : challenges.length === 0 ? (
        <p className="text-muted">No challenges match those filters.</p>
      ) : (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {challenges.map((c) => (
            <Link key={c.id} to={`/challenges/${c.id}`}>
              <Card className="h-full cursor-pointer">
                <div className="mb-3 flex items-center gap-2">
                  <Badge>{c.type}</Badge>
                  <Badge>{c.difficulty}</Badge>
                </div>
                <h3 className="mb-2 text-lg font-semibold">{c.title}</h3>
                <p className="text-sm text-muted">Base reward: {c.base_xp} XP</p>
              </Card>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
