# AI Travel Buddy – Smart Itinerary Planner

A full-stack AI-powered travel assistant that generates personalized itineraries based on destination and budget, with backend APIs, web frontend, and mobile app support.

## 📋 Table of Contents

- [Project Overview](#project-overview)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Backend Setup](#backend-setup)
- [Frontend Setup](#frontend-setup)
- [API Documentation](#api-documentation)
- [Environment Variables](#environment-variables)
- [Deployment](#deployment)
- [Contributing](#contributing)

## Project Overview

**AI Travel Buddy** is a smart itinerary planner that:
- ✅ Generates AI-powered trip plans based on destination, budget, and travel style
- ✅ Integrates with Google Maps for attractions and routes
- ✅ Stores itineraries for users with MongoDB
- ✅ Provides travel trend analytics
- ✅ Offers JWT-based authentication with optional Google OAuth
- ✅ Includes a Next.js web portal and Ionic mobile app

### Core Features

1. **AI Itinerary Generator** – Enter destination + budget → get detailed trip plan
2. **Google Maps Integration** – Find nearby attractions and calculate travel routes
3. **User Itineraries** – Save, view, and manage trips
4. **Travel Analytics** – Track top destinations, average budgets, and travel trends
5. **Mobile Offline Access** – Ionic React app with local storage

## Tech Stack

### Backend
- **Framework**: Flask (Python)
- **Database**: MongoDB
- **Authentication**: JWT
- **AI**: OpenAI API (GPT-3.5 Turbo)
- **Maps**: Google Maps API
- **Hosting**: Docker + AWS/GCP

### Frontend
- **Web**: Next.js 16 (React 19, TypeScript)
- **Styling**: Tailwind CSS v4
- **State Management**: React Context API
- **Mobile**: Ionic React (React Native alternative)
- **Deployment**: Vercel

### DevOps
- **Containerization**: Docker
- **Package Manager**: npm (monorepo workspace)
- **Version Control**: Git

## Project Structure

```
ai-travel-buddy/
├── backend/                  # Flask backend API
│   ├── models/              # MongoDB data models
│   ├── routes/              # API endpoints
│   ├── services/            # Business logic (AI, Maps, Auth)
│   ├── utils/               # Helper functions
│   ├── config.py            # Configuration
│   ├── database.py          # MongoDB connection
│   ├── main.py              # Flask app entry point
│   └── requirements.txt      # Python dependencies
│
├── apps/
│   ├── web/                 # Next.js web app
│   │   ├── app/            # App Router pages
│   │   ├── pages/          # Pages Router (legacy, can remove)
│   │   ├── styles/         # Global styles
│   │   └── tailwind.config.js
│   │
│   └── mobile/             # Ionic React mobile app
│       ├── src/
│       └── ionic.config.json
│
├── shared/                  # Shared code (API clients, components)
│   ├── api/                # API client functions
│   ├── components/         # Shared React components
│   └── package.json
│
├── package.json             # Root monorepo config
└── README.md               # This file
```

## Getting Started

### Prerequisites

- **Node.js**: v18+ (for frontend and monorepo management)
- **Python**: 3.8+ (for backend)
- **MongoDB**: Local or cloud (MongoDB Atlas)
- **Git**: For version control

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/ai-travel-buddy.git
   cd ai-travel-buddy
   ```

2. **Install root dependencies**
   ```bash
   npm install
   ```

3. **Set up environment variables** (see [Environment Variables](#environment-variables) section)

4. **Start backend and frontend**
   ```bash
   # Terminal 1: Backend (Python)
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   python main.py

   # Terminal 2: Frontend (Node.js)
   npm run dev
   ```

5. **Access the application**
   - Web: http://localhost:3000
   - Backend API: http://localhost:8000
   - API docs: http://localhost:8000/api/health

## Backend Setup

### 1. Install Dependencies

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment

Create `.env` file in `backend/`:

```env
FLASK_ENV=development
MONGODB_URI=mongodb://localhost:27017/ai_travel_buddy
JWT_SECRET=your-secret-key-here
OPENAI_API_KEY=sk-your-openai-key
GOOGLE_MAPS_API_KEY=your-google-maps-key
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

### 3. Start MongoDB

**Local MongoDB:**
```bash
mongod  # Starts on port 27017
```

**Or use MongoDB Atlas (cloud):**
- Create account at https://www.mongodb.com/cloud/atlas
- Update `MONGODB_URI` in `.env`

### 4. Run Backend

```bash
python main.py
```

The API will be available at http://localhost:8000

**Health check:**
```bash
curl http://localhost:8000/api/health
```

### API Endpoints

#### Authentication
- `POST /api/auth/signup` – Register user
- `POST /api/auth/login` – Login user
- `GET /api/auth/me` – Get current user (requires token)

#### Itineraries
- `POST /api/itinerary/generate` – Generate AI itinerary
- `GET /api/itinerary/user/<user_id>` – Get user's itineraries
- `GET /api/itinerary/<itinerary_id>` – Get specific itinerary
- `DELETE /api/itinerary/<itinerary_id>` – Delete itinerary

#### Analytics
- `GET /api/analytics/trends` – Get travel trends
- `GET /api/analytics/user/<user_id>/stats` – Get user stats

#### Maps
- `GET /api/maps/nearby-attractions?location=Paris` – Get nearby attractions
- `GET /api/maps/geocode?address=Eiffel Tower` – Geocode address
- `GET /api/maps/distance?origin=Paris&destination=Lyon` – Calculate distance

## Frontend Setup

### 1. Install Dependencies

```bash
npm install
```

This installs dependencies for the entire monorepo (root, `apps/web`, `apps/mobile`, `shared`).

### 2. Configure Environment

Create `apps/web/.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

### 3. Run Development Server

```bash
npm run dev
```

The web app will be available at http://localhost:3000

### 4. Build for Production

```bash
npm run build:web
npm run start
```

## API Documentation

### Generate Itinerary

**Request:**
```bash
POST /api/itinerary/generate
Authorization: Bearer <token>
Content-Type: application/json

{
  "destination": "Paris, France",
  "budget": 2000,
  "days": 5,
  "travel_style": "cultural"
}
```

**Response:**
```json
{
  "message": "Itinerary generated successfully",
  "itinerary": {
    "_id": "507f1f77bcf86cd799439011",
    "destination": "Paris, France",
    "budget": { "amount": 2000, "currency": "USD" },
    "travel_duration": 5,
    "travel_style": "cultural",
    "itinerary": {
      "title": "5 Days in Paris",
      "days": [...]
    },
    "created_at": "2024-01-15T10:30:00Z"
  }
}
```

### Get Travel Trends

**Request:**
```bash
GET /api/analytics/trends
```

**Response:**
```json
{
  "top_destinations": [
    { "_id": "Paris", "count": 45, "avg_budget": 2150 },
    { "_id": "Tokyo", "count": 38, "avg_budget": 2500 }
  ],
  "budget_by_travel_style": [
    { "_id": "leisure", "avg_budget": 1800, "count": 25 },
    { "_id": "adventure", "avg_budget": 2200, "count": 15 }
  ]
}
```

## Environment Variables

### Backend (`.env` in `backend/`)

| Variable | Description | Example |
|----------|-------------|---------|
| `FLASK_ENV` | Environment | `development` or `production` |
| `MONGODB_URI` | MongoDB connection | `mongodb://localhost:27017/ai_travel_buddy` |
| `JWT_SECRET` | JWT signing key | `your-super-secret-key` |
| `OPENAI_API_KEY` | OpenAI API key | `sk-...` |
| `GOOGLE_MAPS_API_KEY` | Google Maps key | `AIzaSy...` |
| `CORS_ORIGINS` | Allowed origins | `http://localhost:3000,http://localhost:5173` |

### Frontend (`.env.local` in `apps/web/`)

| Variable | Description | Example |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | Backend API URL | `http://localhost:8000/api` |

## Deployment

### Backend (Docker)

1. **Build Docker image:**
   ```bash
   cd backend
   docker build -t ai-travel-buddy-backend .
   ```

2. **Run container:**
   ```bash
   docker run -p 8000:8000 \
     -e MONGODB_URI=<your-mongodb-uri> \
     -e OPENAI_API_KEY=<your-key> \
     -e GOOGLE_MAPS_API_KEY=<your-key> \
     ai-travel-buddy-backend
   ```

3. **Deploy to AWS/GCP/Azure** (e.g., Cloud Run, App Engine, EC2)

### Frontend (Vercel)

1. **Push to GitHub**
   ```bash
   git push origin main
   ```

2. **Connect to Vercel:**
   - Go to https://vercel.com/new
   - Select the GitHub repo
   - Set environment variables (from `.env.local`)
   - Deploy

3. **Set production environment variables:**
   - `NEXT_PUBLIC_API_URL=https://your-backend.com/api`

## Features

### Implemented ✅
- ✅ User authentication (signup, login, JWT)
- ✅ AI-powered itinerary generation
- ✅ MongoDB data persistence
- ✅ Google Maps integration
- ✅ Travel trend analytics
- ✅ Next.js web portal
- ✅ Responsive design (Tailwind CSS v4)
- ✅ API error handling & validation

### In Progress / Planned 🚀
- 🚀 Google OAuth integration
- 🚀 Ionic React mobile app (offline storage, push notifications)
- 🚀 Expense tracker
- 🚀 AI-based packing checklist
- 🚀 Social sharing of itineraries
- 🚀 Hotel/flight booking integration

### Removed Features ❌
- ❌ WordPress plugin (removed - see `FEATURE_REMOVAL_DECISION.md`)
- ❌ BigQuery analytics (removed - MongoDB analytics sufficient)

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License – see the LICENSE file for details.

## Support

For questions or issues:
- 📧 Email: support@aitravel.buddy
- 💬 GitHub Issues: https://github.com/yourusername/ai-travel-buddy/issues
- 📚 Documentation: https://docs.aitravel.buddy

---

**Built with ❤️ for travelers everywhere**
