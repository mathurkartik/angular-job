import { Briefcase, Building, Code2, Cpu, Globe, Rocket, Terminal } from "lucide-react";
import { CompanyCategory } from "../types";
import "./Sidebar.css";

interface SidebarProps {
  activeCategory: string;
  setActiveCategory: (category: string) => void;
}

export function Sidebar({ activeCategory, setActiveCategory }: SidebarProps) {
  const categories = [
    { id: "all", label: "All Jobs", icon: Briefcase },
    { id: CompanyCategory.MAIN, label: "Tier 1 & 2 (Main)", icon: Rocket },
    { id: CompanyCategory.INDIAN_PRODUCT, label: "Indian Product", icon: Cpu },
    { id: CompanyCategory.SERVICE, label: "Service / Consult", icon: Building },
  ];

  return (
    <aside className="sidebar glass-panel">
      <div className="sidebar-header">
        <div className="logo-container">
          <Code2 className="logo-icon" size={28} />
          <h2>Angular<span className="text-gradient">Hunt</span></h2>
        </div>
        <p className="subtitle">Automated Job Engine</p>
      </div>

      <nav className="sidebar-nav">
        {categories.map((cat) => {
          const Icon = cat.icon;
          return (
            <button
              key={cat.id}
              className={`nav-item ${activeCategory === cat.id ? "active" : ""}`}
              onClick={() => setActiveCategory(cat.id)}
            >
              <Icon size={18} />
              <span>{cat.label}</span>
            </button>
          );
        })}
      </nav>

      <div className="sidebar-footer">
        <div className="status-indicator">
          <span className="pulse-dot"></span>
          <span>System Online</span>
        </div>
      </div>
    </aside>
  );
}
