# OpenFinance-Col

[![CI](https://github.com/juanchobanano/openfinance-colombia/actions/workflows/ci.yml/badge.svg)](https://github.com/juanchobanano/openfinance-colombia/actions/workflows/ci.yml)
[![AGPL License](https://img.shields.io/badge/license-AGPL--3.0-blue.svg)](./LICENSE)
[![Join our Discord](https://img.shields.io/discord/1234567890?label=Discord&logo=discord&color=7289DA)](https://discord.gg/e8hgBYSq)


> **Plataforma open-source para el ecosistema Open Finance en Colombia**
>
> Comienza hoy con extractos bancarios y scraping de datos financieros. Mañana, seremos interoperables con APIs oficiales.

---

## 🚀 Nuestra visión

Convertirnos en la **infraestructura comunitaria de referencia** para todo el ecosistema Open Finance en Colombia.

Nuestro enfoque incluye:

* Bancos, cooperativas, billeteras.
* Tarjetas de crédito, CDT, cuentas corrientes y de ahorro.
* Datos de inversiones, seguros, y pensiones en el futuro.

Queremos democratizar el acceso a los datos financieros, con una arquitectura modular, segura, auditable y lista para migrar a APIs bancarias tan pronto estén disponibles.

## 📊 Estado actual `v0.1.0`

* Receptor de correos (`forward@openfinance-col.io`) para extractos PDF.
* Parser funcional para extractos Bancolombia.
* Scraper de tasas de CDT (Bancolombia y Davivienda).
* API REST (`/transactions`, `/products`).
* Interfaz web (Next.js 15) con resumen de transacciones y tasas.
* Arquitectura dockerizada lista para desarrollo local.

📌 [Ver nuestro Roadmap público](https://github.com/users/Juanchobanano/projects/1)


## 👩‍💻 Cómo empezar

```bash
git clone https://github.com/tuusuario/openfinance-col.git
cd openfinance-col
docker compose up --build
```

Accede a `http://localhost:3000` para la interfaz, o `http://localhost:8000/docs` para la API.

## 🧱 Tecnologías principales

* Backend: Python + FastAPI + PostgreSQL + Celery
* Frontend: Next.js 15 + TailwindCSS
* Scraping/parsers: Python + Playwright

## 🛣️ Roadmap

* `v0.2.0` ➤ Parsers Nequi y Davivienda
* `v0.3.0` ➤ Flujo de consentimiento y log de auditoría
* `v0.4.0` ➤ Abstracción de conectores tipo `BankConnector`
* `v1.0.0` ➤ Primer API oficial de banco integrado

## 🙌 Súmate a la comunidad

Este proyecto está hecho por y para desarrolladores, fintechs, analistas y entusiastas del futuro financiero en Colombia.

* Explora y comenta los issues activos.
* Crea PRs (Pull Requests) o abre nuevos issues.
* Mejora los parsers existentes o crea uno nuevo.
* Únete al canal de Discord (en construcción).

Lee nuestra [guía de contribución](./CONTRIBUTING.md) para comenzar.

## 🔒 Licencia

Este proyecto está licenciado bajo **AGPL-3.0**. Consulta [LICENSE](./LICENSE) para más información.

---

> Creado con ❤️ por la comunidad OpenFinance-Col. Nuestra misión es abrir el acceso a los datos financieros para todos los colombianos.
