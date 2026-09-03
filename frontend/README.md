# Frontend

Vue 3 + TypeScript UI for the Home Energy Advisor. For setup via Docker,
assumptions, and the AI usage log, see the [root README](../README.MD).

## Run

```bash
npm install
npm run dev
```

Runs on `http://localhost:5173` and expects the backend at `http://localhost:8000`
(override with `VITE_API_BASE_URL`).

## Commands

```bash
npm run test          # vitest
npm run type-check    # vue-tsc
npm run lint          # eslint (add --fix, or use `npm run lint:fix`)
npm run format        # prettier --write
npm run build          # type-check + production build
```

## Layout

```
src/
  api/         fetch wrapper + typed API client
  components/  HomeForm, AdviceList, RecommendationCard
  stores/      Pinia store (home profile + advice state)
  types/       TS types mirroring the backend's Pydantic schemas
  App.vue      wires the form -> store -> results together
```
