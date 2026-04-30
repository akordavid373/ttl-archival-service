import React from "react";
import { Link, useLocation } from "react-router-dom";
import { ChevronRight, Home } from "lucide-react";

export function Breadcrumbs() {
  const location = useLocation();
  const pathnames = location.pathname.split("/").filter((x) => x);

  return (
    <nav className="flex items-center space-x-2 text-xs font-medium text-muted-foreground mb-6">
      <Link
        to="/"
        className="flex items-center hover:text-primary transition-colors hover:bg-primary/5 px-2 py-1 rounded-md"
      >
        <Home className="h-3.5 w-3.5 mr-1" />
        <span>Dashboard</span>
      </Link>

      {pathnames.map((name, index) => {
        const routeTo = `/${pathnames.slice(0, index + 1).join("/")}`;
        const isLast = index === pathnames.length - 1;
        const formattedName =
          name.charAt(0).toUpperCase() + name.slice(1).replace(/-/g, " ");

        return (
          <React.Fragment key={name}>
            <ChevronRight className="h-3.5 w-3.5 text-muted-foreground/40" />
            {isLast ? (
              <span className="text-foreground font-bold px-2 py-1 bg-accent/50 rounded-md ring-1 ring-border/50">
                {formattedName}
              </span>
            ) : (
              <Link
                to={routeTo}
                className="hover:text-primary transition-colors hover:bg-primary/5 px-2 py-1 rounded-md"
              >
                {formattedName}
              </Link>
            )}
          </React.Fragment>
        );
      })}
    </nav>
  );
}
