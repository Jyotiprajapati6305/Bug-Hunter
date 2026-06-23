import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { useAuth } from "@/hooks/useAuth";
import { cn } from "@/lib/utils";

const navItems = [
  { to: "/dashboard", label: "Dashboard" },
  { to: "/challenges", label: "Challenges" },
];

export function AppLayout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  async function handleLogout() {
    await logout();
    navigate("/login");
  }

  return (
    <div className="min-h-screen bg-background text-foreground">
      <header className="sticky top-0 z-10 border-b border-border bg-background/80 backdrop-blur-md">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          <div className="flex items-center gap-8">
            <span className="text-lg font-bold tracking-tight">
              Bug Hunter <span className="text-muted">Arena</span>
            </span>
            <nav className="flex items-center gap-1">
              {navItems.map((item) => (
                <NavLink
                  key={item.to}
                  to={item.to}
                  className={({ isActive }) =>
                    cn(
                      "rounded-md px-3 py-1.5 text-sm font-medium transition-colors duration-200",
                      isActive ? "bg-card text-foreground" : "text-muted hover:text-foreground"
                    )
                  }
                >
                  {item.label}
                </NavLink>
              ))}
            </nav>
          </div>
          <div className="flex items-center gap-4">
            {user && (
              <div className="flex items-center gap-2 text-sm">
                <span className="text-muted">{user.username}</span>
                <span className="rounded-full border border-border bg-surface px-2 py-0.5 text-xs uppercase tracking-wide text-muted">
                  {user.role}
                </span>
              </div>
            )}
            <button
              onClick={handleLogout}
              className="rounded-md border border-border bg-card px-3 py-1.5 text-sm font-medium text-foreground transition-colors duration-200 hover:bg-[#202020]"
            >
              Log out
            </button>
          </div>
        </div>
      </header>
      <main className="mx-auto max-w-6xl px-6 py-10">
        <Outlet />
      </main>
    </div>
  );
}
