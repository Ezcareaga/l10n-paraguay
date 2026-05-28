// Conventional Commits config for l10n-paraguay.
// Consumed by .github/workflows/commitlint.yml (wagoid/commitlint-github-action@v6).
// Locally usable with `npx commitlint --from=origin/main`.

module.exports = {
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
    "scope-enum": [
      1, // 1 = warning (not error) — scope is optional
      "always",
      [
        "l10n_py_base",
        "l10n_py_account",
        "pre-commit",
        "ci",
        "docs",
        "", // allow empty scope
      ],
    ],
    "subject-case": [2, "never", ["upper-case", "pascal-case", "start-case"]],
    "header-max-length": [2, "always", 100],
    "body-leading-blank": [2, "always"],
    "footer-leading-blank": [2, "always"],
  },
};
