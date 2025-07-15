# Guía de contribución a OpenFinance-Col

🚀 Gracias por tu interés en contribuir a OpenFinance-Col. Esta guía te ayudará a comenzar, ya sea que quieras arreglar un bug, crear un parser nuevo, mejorar la documentación o proponer nuevas ideas.

---

## 📊 Antes de comenzar

1. Lee nuestro [Código de Conducta](./CODE_OF_CONDUCT.md).
2. Si tienes dudas, abre una *Discussion* o escríbenos por Discord.
3. Busca issues marcados como `good first issue` o `help wanted`.

---

## 🎓 Requisitos previos

* Python 3.12+
* Node.js 20+
* Docker + Docker Compose
* `make`, `poetry`, `pnpm` (opcional pero recomendado)

---

## 🚀 Pasos para clonar y correr localmente

```bash
git clone https://github.com/openfinance-col/openfinance-col.git
cd openfinance-col
docker compose up --build
```

Esto iniciará:

* API FastAPI en `localhost:8000`
* Frontend Next.js en `localhost:3000`

---

## 📄 Estructura del repositorio

```
openfinance-col/
├ apps/
│  ├ backend/        # FastAPI
│  └ frontend/       # Next.js
├ packages/
│  ├ parsers/        # Bancolombia, Nequi...
│  ├ product-scraper/
│  └ common-schemas/
├ docs/              # Docusaurus (próximamente)
├ docker-compose.yml
└ .github/           # Workflows y plantillas
```

---

## 🔧 Estilo de código y buenas prácticas

* Python: `black`, `ruff`, `mypy`
* JS/TS: `prettier`, `eslint`
* Commits: usar convenciones tipo `feat:`, `fix:`, `docs:`
* Abre PRs pequeños y enfocados. Agrega tests cuando sea posible.

---

## 📝 Cómo contribuir

1. Haz un fork del repositorio.
2. Crea una nueva rama: `git checkout -b feat/nombre-cambio`.
3. Realiza tus cambios y haz commit.
4. Sube tu rama: `git push origin feat/nombre-cambio`
5. Abre un Pull Request (PR) hacia `main`.
6. Espera revisión, responde comentarios y ajusta si es necesario.

---

## ✉️ Reportar errores o sugerencias

* Usa el tab de **Issues** para reportar bugs.
* Marca sugerencias con `enhancement`.

---

## 🌟 Gracias

Cada aporte ayuda a que OpenFinance-Col crezca como proyecto y como comunidad. ¡Estamos felices de tenerte aquí!
