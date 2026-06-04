// Conventional Commits config for l10n-paraguay.
// Consumed by .github/workflows/commitlint.yml (wagoid/commitlint-github-action@v6).
// Locally usable with `npx commitlint --from=origin/main`.
//
// ESM (.mjs) is required by wagoid v6.2.1+ — .js extension is rejected.
//
// Política de scopes: a partir de Phase 2 Wave 4 (compliance Ley 7593/2025) el
// workflow GSD emite scopes dinámicos por phase/plan/ticket (`phase-02`,
// `02-03`, `sec-06`, etc.) además de los scopes técnicos por módulo. Mantener
// un allowlist cerrado obliga a editarlo cada vez que se abre una phase/plan
// nueva, lo que rompe la atomicidad del commit del executor. Solución: dejar
// `scope-enum` como recomendación libre (rule disabled) y confiar en
// `type-enum` + revisión humana del PR para gobernanza. Conventional Commits
// no exige scope-enum; OCA upstream tampoco lo hace.
//
// Límites de longitud:
// - header-max-length: 120 (cubre los headers generados por el merger de
//   worktrees GSD del tipo `chore: merge executor worktree
//   (worktree-agent-<hash>) — Plan <NN-NN> <descripción>`).
// - body-max-line-length: disabled. Los commits del executor GSD incluyen
//   stats inline ("Bandit 1.9.4 -lll -iii on addons/ (2228 LOC): 0 HIGH
//   findings; full audit also 0 MEDIUM/LOW → no BUGS_BACKLOG.md entry"),
//   comandos completos, URLs largas, y referencias `[[memory-name]]`. El
//   line-wrap a 120 mutila esa información sin agregar legibilidad.

export default {
  extends: ["@commitlint/config-conventional"],
  rules: {
    "type-enum": [
      2,
      "always",
      [
        "feat", // new feature
        "fix", // bug fix
        "refactor", // code change neither feat nor fix
        "test", // adding / fixing tests
        "docs", // documentation only
        "chore", // tooling, infra, no code change
        "style", // formatting, no semantic change
        "perf", // performance improvement
        "build", // build system / dependencies
        "ci", // CI/CD config
        "revert", // revert previous commit
      ],
    ],
    "scope-enum": [0], // disabled — see header note (GSD scopes are dynamic)
    "subject-case": [2, "never", ["upper-case", "pascal-case", "start-case"]],
    "header-max-length": [2, "always", 120],
    "body-max-line-length": [0], // disabled — see header note (GSD stats/commands)
    "body-leading-blank": [2, "always"],
    "footer-leading-blank": [2, "always"],
  },
};
