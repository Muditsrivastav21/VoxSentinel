import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Route, Routes, Navigate } from "react-router-dom";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import AppLayout from "@/components/AppLayout";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import AnalyzeCall from "./pages/AnalyzeCall";
import CallHistory from "./pages/CallHistory";
import CallDetail from "./pages/CallDetail";
import Leaderboard from "./pages/Leaderboard";
import Trends from "./pages/Trends";
import NotFound from "./pages/NotFound";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Sonner />
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Login />} />
          <Route element={<AppLayout />}>
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/analyze" element={<AnalyzeCall />} />
            <Route path="/history" element={<CallHistory />} />
            <Route path="/call/:id" element={<CallDetail />} />
            <Route path="/leaderboard" element={<Leaderboard />} />
            <Route path="/trends" element={<Trends />} />
          </Route>
          <Route path="*" element={<NotFound />} />
        </Routes>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
