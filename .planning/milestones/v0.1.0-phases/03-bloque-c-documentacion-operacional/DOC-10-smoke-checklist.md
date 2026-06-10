## DOC-10 — Smoke test de documentación (dev externo)

Un desarrollador **sin contexto previo del repo** sigue únicamente `CONTRIBUTING.md`
en su propia máquina y registra el resultado acá. El objetivo es validar que la
documentación operacional alcanza para arrancar de cero. **No simular**: lo corre una
persona real de forma asíncrona. Esta UAT **no bloquea** el avance a Phase 4 (D-16).

### Checklist

- [ ] `git clone` del repo termina sin error
- [ ] `docker compose -f infra/docker-compose.yml up -d` levanta limpio
- [ ] http://localhost:8069 responde en el navegador
- [ ] Creación de la base de datos funciona (Name `l10n_py_dev`, Country Paraguay, Demo NO)
- [ ] `l10n_py_base` se instala sin errores
- [ ] `l10n_py_account` se instala sin errores
- [ ] El runner de tests de Odoo reporta **97 tests verdes** (comando de `CONTRIBUTING.md`)

### Fricciones encontradas

> El tester documenta acá cualquier paso confuso, comando que faltó, dependencia no
> declarada, o divergencia CI-vs-local. Cada fricción es input para mejorar
> `CONTRIBUTING.md` / `docs/71_DEPLOYMENT.md`.

_(libre — completar durante la corrida)_
