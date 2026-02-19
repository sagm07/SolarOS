# ☀️ SolarOS — Sustainability-Aware Decision Engine for Solar Farms

**Intelligent, data-driven cleaning recommendations for solar panel operations using NASA satellite data and multi-objective optimization.**

[![Next.js](https://img.shields.io/badge/Next.js-14-black)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green)](https://fastapi.tiangolo.com/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-blue)](https://www.typescriptlang.org/)
[![Python](https://img.shields.io/badge/Python-3.10+-blue)](https://www.python.org/)

---

## 🚀 Live Demo

- **Frontend (Vercel):** [https://solaros.vercel.app](https://solaros.vercel.app)
- **Backend (Render):** [https://solaros.onrender.com/docs](https://solaros.onrender.com/docs)

---

## 🚀 Live Demo

- **Frontend (Vercel):** [https://solaros.vercel.app](https://solaros.vercel.app)
- **Backend (Render):** [https://solaros.onrender.com/docs](https://solaros.onrender.com/docs)

---

## 🌍 Overview

SolarOS is a **full-stack SaaS application** that helps solar farm operators optimize cleaning schedules by balancing:

- **Energy Output Recovery** — Maximize kWh generation
- **Carbon Footprint** — Minimize environmental impact
- **Water Conservation** — Reduce water usage through intelligent forecasting
- **Economic Efficiency** — Optimize cleaning ROI

Built for hackathons, research demonstrations, and production deployment on **Vercel** (frontend) + **Render** (backend).

---

## ✨ Features

### 🎯 Core Intelligence

- **Digital Twin Modeling** — Physics-based degradation simulation
- **NASA POWER API Integration** — Real-time satellite environmental data
- **Multi-Objective Optimization** — Balance profit, carbon, and water usage
- **Autonomous Recommendations** — Data-driven cleaning date suggestions

### 🚀 Dashboard Features

- **Rain Intelligence** — Defer cleaning when rain is forecast to save water
- **Multi-Farm Portfolio Optimizer** — Optimize resource allocation across multiple sites
- **Live Analysis** — Interactive parameter tuning with instant feedback
- **Production-Ready Analytics** — Professional charts and metrics visualization

---

## 🛠️ Tech Stack

### Frontend
- **Next.js 14** (App Router)
- **TypeScript** — Type-safe development
- **Tailwind CSS** — Utility-first styling
- **Framer Motion** — Smooth, performant animations
- **Recharts** — Data visualization

### Backend
- **FastAPI** — High-performance Python API
- **NumPy & Pandas** — Scientific computing
- **NASA POWER API** — Satellite weather data
- **Uvicorn** — ASGI server

---

## 🚀 Local Setup

### Prerequisites

- **Node.js 18+**
- **Python 3.10+**
- **Git**

### Frontend Setup

```bash
cd web
npm install
npm run dev
```

Frontend runs at: **http://localhost:3000**

### Backend Setup

```bash
# From project root
pip install -r backend/requirements.txt
uvicorn backend.main:app --reload
```

Backend runs at: **http://localhost:8000**

**API Documentation**: http://localhost:8000/docs

---

## 📦 Environment Variables

### Frontend (`.env.local`)

```bash
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

For production on Vercel:
```bash
NEXT_PUBLIC_API_BASE_URL=https://your-backend-url.onrender.com
```

---

## 🌐 Deployment

### Deploy Backend (Render)

1. Create new **Web Service** on [Render](https://render.com)
2. Connect GitHub repository
3. **Start Command:**
   ```bash
   uvicorn backend.main:app --host 0.0.0.0 --port $PORT
   ```
4. Deploy and copy the URL

### Deploy Frontend (Vercel)

1. Import repository to [Vercel](https://vercel.com)
2. Set **Root Directory:** `web`
3. **Environment Variable:**
   ```
   NEXT_PUBLIC_API_BASE_URL=https://your-backend-url.onrender.com
   ```
4. Deploy

---

## 📊 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/analyze` | GET | Solar cleaning analysis |
| `/rain-forecast` | GET | Rain intelligence |
| `/optimize-farms` | POST | Multi-farm optimization |

**Full API docs**: http://localhost:8000/docs

---

## 🎨 Features Showcase

### Intelligent Cleaning Recommendations
- Analyzes 30 days of solar farm data
- Recommends optimal cleaning date
- Calculates energy gain, carbon savings, and ROI

### Rain Intelligence
- Checks 7-day weather forecast
- Defers cleaning if rain expected
- Estimates natural dust reduction and water savings

### Multi-Farm Portfolio Optimization
- Optimize resource allocation across multiple farms
- Balance profit, carbon offset, or water scarcity constraints
- Smart selection based on cleaning ROI

---

## 📁 Project Structure

```
SolarOS/
├── backend/
│   ├── main.py              # FastAPI application
│   └── requirements.txt     # Python dependencies
├── ml/
│   ├── data_loader.py       # NASA API integration
│   ├── scenario_analysis.py # Core optimization logic
│   └── ...                  # ML models
├── web/
│   ├── src/
│   │   ├── app/             # Next.js pages
│   │   └── components/      # React components
│   ├── public/              # Static assets
│   └── package.json         # Node dependencies
├── .gitignore
└── README.md
```

---

## 🧪 Testing

### Frontend Build

```bash
cd web
npm run build
```

### Backend Health Check

```bash
curl http://localhost:8000/health
```

---

## 🔒 Security

- ✅ No API keys committed
- ✅ Environment variables excluded via `.gitignore`
- ✅ CORS configured for production
- ✅ Input validation with FastAPI Pydantic models

---

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

---

## 👥 Contributing

Contributions, issues, and feature requests are welcome!

---

## 🙏 Acknowledgments

- **NASA POWER API** for environmental data
- **Vercel** for frontend hosting
- **Render** for backend deployment

---

## 📬 Contact

**Project Link:** [https://github.com/yourusername/SolarOS](https://github.com/sagm07/SolarOS)

---

**Built with ❤️ for sustainable energy infrastructure**
