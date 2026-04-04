import { useState } from "react";
import { Outlet, useLocation, Link, useNavigate } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import {
  LayoutDashboard, Phone, History, Search, ChevronLeft, ChevronRight, LogOut,
} from "lucide-react";
import VoxLogo from "./VoxLogo";
import ThemeToggle from "./ThemeToggle";

const navItems = [
  { label: "Dashboard", path: "/dashboard", icon: LayoutDashboard },
  { label: "Analyze Call", path: "/analyze", icon: Phone },
  { label: "Call History", path: "/history", icon: History },
];

const AppLayout = () => {
  const [collapsed, setCollapsed] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();

  const breadcrumb = navItems.find((n) => location.pathname.startsWith(n.path))?.label ?? "Dashboard";

  const handleLogout = () => {
    navigate("/");
  };

  return (
    <div className="flex h-screen overflow-hidden bg-background">
      {/* Sidebar with glassmorphism */}
      <motion.aside
        animate={{ width: collapsed ? 64 : 220 }}
        transition={{ duration: 0.25, ease: "easeInOut" }}
        className="relative z-20 flex flex-col border-r border-border bg-card/80 backdrop-blur-xl"
      >
        <div className="flex h-14 items-center gap-2 px-4">
          <VoxLogo className="h-7 w-7 shrink-0" />
          <AnimatePresence>
            {!collapsed && (
              <motion.span
                initial={{ opacity: 0, width: 0 }}
                animate={{ opacity: 1, width: "auto" }}
                exit={{ opacity: 0, width: 0 }}
                className="overflow-hidden whitespace-nowrap text-sm font-semibold tracking-tight text-foreground"
              >
                VoxSentinel
              </motion.span>
            )}
          </AnimatePresence>
        </div>

        <nav className="mt-2 flex-1 space-y-1 px-2">
          {navItems.map((item) => {
            const active = location.pathname.startsWith(item.path);
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`group flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors active:scale-[0.98] ${
                  active
                    ? "bg-primary/10 text-primary"
                    : "text-muted-foreground hover:bg-accent hover:text-foreground"
                }`}
              >
                <item.icon className="h-4 w-4 shrink-0" />
                <AnimatePresence>
                  {!collapsed && (
                    <motion.span
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      exit={{ opacity: 0 }}
                      className="overflow-hidden whitespace-nowrap"
                    >
                      {item.label}
                    </motion.span>
                  )}
                </AnimatePresence>
              </Link>
            );
          })}
        </nav>

        {/* Logout + Collapse */}
        <div className="space-y-1 px-2 pb-4">
          <button
            onClick={handleLogout}
            className="flex w-full items-center gap-3 rounded-md px-3 py-2 text-sm font-medium text-muted-foreground transition-colors hover:bg-destructive/10 hover:text-destructive active:scale-[0.98]"
          >
            <LogOut className="h-4 w-4 shrink-0" />
            <AnimatePresence>
              {!collapsed && (
                <motion.span
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="overflow-hidden whitespace-nowrap"
                >
                  Logout
                </motion.span>
              )}
            </AnimatePresence>
          </button>
          <button
            onClick={() => setCollapsed(!collapsed)}
            className="flex w-full h-8 items-center justify-center rounded-md text-muted-foreground transition-colors hover:bg-accent hover:text-foreground"
          >
            {collapsed ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
          </button>
        </div>
      </motion.aside>

      {/* Main */}
      <div className="flex flex-1 flex-col overflow-hidden">
        {/* Header with glassmorphism */}
        <header className="flex h-14 shrink-0 items-center justify-between border-b border-border bg-card/80 backdrop-blur-xl px-6">
          <div className="flex items-center gap-2 text-sm">
            <span className="text-muted-foreground">VoxSentinel</span>
            <span className="text-muted-foreground">/</span>
            <span className="font-medium text-foreground">{breadcrumb}</span>
          </div>
          <div className="flex items-center gap-2">
            <button className="flex h-8 items-center gap-2 rounded-md border border-border bg-background/50 backdrop-blur-sm px-3 text-xs text-muted-foreground transition-colors hover:bg-accent">
              <Search className="h-3.5 w-3.5" />
              <span>Search...</span>
              <kbd className="ml-2 rounded border border-border bg-muted px-1.5 py-0.5 text-[10px] font-medium">⌘K</kbd>
            </button>
            <ThemeToggle />
          </div>
        </header>

        {/* Content */}
        <main className="flex-1 overflow-y-auto p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default AppLayout;
