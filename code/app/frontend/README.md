# BXS Dashboard Frontend

React + Vite + Tailwind CSS dashboard for Bitcoin Seconds (BXS) metrics.

## Development

```bash
cd code/app/frontend
npm install
npm run dev
```

The dev server will proxy API requests to `http://localhost:8080`.

## Build

```bash
npm run build
```

This builds the React app to `code/app/static/` which is served by FastAPI.

## Features

- Real-time metrics display
- Sparklines for key metrics (W, i, μ, f)
- Negative SSR visual warnings
- Baseline tooltips (A₀, I₀)
- Responsive design
- Auto-refresh every 60 seconds

