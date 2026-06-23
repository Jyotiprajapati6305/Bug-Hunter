import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { challengeService } from "@/services/challengeService";
import { useAuth } from "@/hooks/useAuth";
import type { BugSubmitPayload, BugSubmitResult, ChallengeDetail, ChallengeSession } from "@/services/types";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Input, Label, Textarea } from "@/components/ui/Input";

const SEVERITIES = ["critical", "high", "medium", "low"] as const;
const PRIORITIES = ["urgent", "high", "normal", "low"] as const;

const emptyForm: BugSubmitPayload = {
  title: "",
  description: "",
  steps_to_reproduce: "",
  actual_result: "",
  expected_result: "",
  severity: "medium",
  priority: "normal",
};

export function ChallengeDetailPage() {
  const { id } = useParams<{ id: string }>();
  const { user } = useAuth();
  const [challenge, setChallenge] = useState<ChallengeDetail | null>(null);
  const [session, setSession] = useState<ChallengeSession | null>(null);
  const [form, setForm] = useState<BugSubmitPayload>(emptyForm);
  const [result, setResult] = useState<BugSubmitResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [starting, setStarting] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (!id) return;
    challengeService.get(id).then(setChallenge);
  }, [id]);

  async function handleStart() {
    if (!id) return;
    setStarting(true);
    setError(null);
    try {
      const s = await challengeService.start(id);
      setSession(s);
    } catch (err: any) {
      setError(err?.response?.data?.detail ?? "Could not start challenge.");
    } finally {
      setStarting(false);
    }
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!id) return;
    setSubmitting(true);
    setError(null);
    try {
      const res = await challengeService.submitBug(id, form);
      setResult(res);
    } catch (err: any) {
      setError(err?.response?.data?.detail ?? "Could not submit bug report.");
    } finally {
      setSubmitting(false);
    }
  }

  if (!challenge) {
    return <p className="text-muted">Loading challenge...</p>;
  }

  const canSubmitBug = user?.role === "tester";

  return (
    <div className="space-y-6">
      <div>
        <div className="mb-3 flex items-center gap-2">
          <Badge>{challenge.type}</Badge>
          <Badge>{challenge.difficulty}</Badge>
          <Badge>{challenge.base_xp} base XP</Badge>
        </div>
        <h1 className="text-2xl font-bold">{challenge.title}</h1>
        <p className="mt-2 whitespace-pre-wrap text-sm text-muted">{challenge.description}</p>
      </div>

      {!session && !result && (
        <Card>
          <p className="mb-4 text-sm text-muted">
            Start the challenge to open a session, then submit a bug report describing what you found.
          </p>
          <Button onClick={handleStart} disabled={starting}>
            {starting ? "Starting..." : "Start Challenge"}
          </Button>
          {error && <p className="mt-3 text-sm text-red-400">{error}</p>}
        </Card>
      )}

      {session && !result && (
        <Card>
          <h2 className="mb-4 text-lg font-semibold">Submit a bug report</h2>
          {!canSubmitBug && (
            <p className="mb-4 text-sm text-red-400">
              Only accounts with the tester role can submit bug reports.
            </p>
          )}
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <Label htmlFor="title">Title</Label>
              <Input
                id="title"
                required
                value={form.title}
                onChange={(e) => setForm({ ...form, title: e.target.value })}
                placeholder="Short summary of the bug"
              />
            </div>
            <div>
              <Label htmlFor="description">Description</Label>
              <Textarea
                id="description"
                required
                value={form.description}
                onChange={(e) => setForm({ ...form, description: e.target.value })}
              />
            </div>
            <div>
              <Label htmlFor="steps">Steps to reproduce</Label>
              <Textarea
                id="steps"
                required
                value={form.steps_to_reproduce}
                onChange={(e) => setForm({ ...form, steps_to_reproduce: e.target.value })}
              />
            </div>
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div>
                <Label htmlFor="actual">Actual result</Label>
                <Textarea
                  id="actual"
                  required
                  value={form.actual_result}
                  onChange={(e) => setForm({ ...form, actual_result: e.target.value })}
                />
              </div>
              <div>
                <Label htmlFor="expected">Expected result</Label>
                <Textarea
                  id="expected"
                  required
                  value={form.expected_result}
                  onChange={(e) => setForm({ ...form, expected_result: e.target.value })}
                />
              </div>
            </div>
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div>
                <Label htmlFor="severity">Severity</Label>
                <select
                  id="severity"
                  className="input-field"
                  value={form.severity}
                  onChange={(e) => setForm({ ...form, severity: e.target.value as any })}
                >
                  {SEVERITIES.map((s) => (
                    <option key={s} value={s}>
                      {s}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <Label htmlFor="priority">Priority</Label>
                <select
                  id="priority"
                  className="input-field"
                  value={form.priority}
                  onChange={(e) => setForm({ ...form, priority: e.target.value as any })}
                >
                  {PRIORITIES.map((p) => (
                    <option key={p} value={p}>
                      {p}
                    </option>
                  ))}
                </select>
              </div>
            </div>
            {error && <p className="text-sm text-red-400">{error}</p>}
            <Button type="submit" disabled={submitting || !canSubmitBug}>
              {submitting ? "Submitting..." : "Submit bug report"}
            </Button>
          </form>
        </Card>
      )}

      {result && (
        <Card>
          <h2 className="mb-2 text-lg font-semibold">Bug submitted</h2>
          <p className="text-sm text-muted">
            "{result.title}" was recorded as <strong className="text-foreground">{result.status}</strong>.
          </p>
          <div className="mt-4 flex items-center gap-4">
            <Badge className="text-base">+{result.xp_awarded} XP awarded</Badge>
            <Badge className="text-base">New total: {result.new_xp_total} XP</Badge>
            <Badge className="text-base">Level {result.new_level}</Badge>
          </div>
        </Card>
      )}
    </div>
  );
}
