"""
Scoring configuration: Pillars, keywords, and weights.
"""

SCORING_PILLARS = {
    "core_stack": {
        "weight": 0.30,
        "keywords": ["angular", "typescript", "rxjs", "javascript", "html", "css", "scss"],
        "full_marks_count": 4   # How many matches = 1.0 for this pillar
    },
    "modern_angular": {
        "weight": 0.25,
        "keywords": ["standalone component", "standalone components", "signals", "angular 17", "angular 18",
                      "angular 19", "ssr", "hydration", "esbuild", "vite"],
        "full_marks_count": 3
    },
    "state_management": {
        "weight": 0.20,
        "keywords": ["ngrx", "ngxs", "akita", "state management", "redux", "store"],
        "full_marks_count": 2
    },
    "testing_quality": {
        "weight": 0.15,
        "keywords": ["jest", "cypress", "karma", "jasmine", "tdd", "unit test",
                      "e2e", "playwright", "testing library", "code review"],
        "full_marks_count": 3
    },
    "scale_enterprise": {
        "weight": 0.10,
        "keywords": ["micro-frontend", "micro-frontends", "module federation", "nx", "monorepo",
                      "ci/cd", "design system", "wcag", "accessibility", "performance"],
        "full_marks_count": 3
    }
}

MIN_SCORE_THRESHOLD = 0.35  # Minimum to include in output
