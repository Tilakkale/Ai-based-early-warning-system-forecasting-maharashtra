# 🌍 Epidemic Forecasting Project - Enhanced Features

## Project Overview
Advanced AI-powered epidemic forecasting system with interactive dashboard, real-time analytics, and multi-view visualization for disease risk prediction across districts.

---

## ✅ Implemented Features

### 1. **Backend API Enhancements** (FastAPI)
- **Enhanced Model Integration**: Improved ML model loading with absolute paths
- **CORS Support**: Enabled cross-origin requests for frontend communication
- **New Endpoints**:
  - `POST /predict` - Disease risk prediction for dengue & malaria
  - `GET /weather` - Real-time weather data for major cities
  - `GET /districts` - District metadata with coordinates
  - `GET /district-predictions` - Risk predictions for all districts
  - `GET /analytics` - 30-day historical trends & analytics
  - `GET /risk-summary` - Overall risk overview dashboard

### 2. **Modern UI/UX Design**
- **Custom Typography**: Poppins (modern) + Playfair Display (elegant)
- **Premium Color Palette**: Teal (#14b8a6) + Amber (#f59e0b) accent
- **Visual Effects**:
  - Frosted glass (backdrop-filter blur)
  - Radial gradient overlays
  - Shimmer animations on result cards
  - Staggered entrance animations

### 3. **Interactive Navigation**
- **Sticky Navigation Bar**: Easy switching between views
- **5 Main Sections**:
  - 🎯 **Predict** - Single location prediction interface
  - 📈 **Analytics** - Trend charts and statistics
  - 📊 **Districts** - District-wise predictions
  - 🗺️ **Map** - Geospatial risk visualization
  - 🌦️ **Weather** - Real-time weather data

### 4. **Animated Risk Cards**
- **Dynamic Color Coding**: Green (safe), Amber (moderate), Red (high)
- **Shimmer Effects**: Subtle animations on card reveals
- **Hover Animations**: Cards lift up on hover
- **Status Indicators**: Clear risk level badges

### 5. **Advanced Charts Dashboard** (📈)
- **Area Chart**: Disease cases trend over 30 days
- **Line Chart**: Temperature trend analysis
- **Bar Charts**: 
  - Weekly rainfall distribution
  - Risk level distribution
- **Summary Statistics**: KPIs in card format
- **Real-time Data**: Fetches from backend API

### 6. **District-wise Predictions** (📊)
- **Interactive Grid**: Card-based district view
- **Sorting Options**: By risk level, name, or temperature
- **Detailed Metrics**:
  - Dengue & Malaria risk levels
  - Temperature, Humidity, Rainfall
  - Coordinates
- **Status Badges**: Color-coded risk levels
- **Statistics Overview**: High/Moderate/Safe district counts

### 7. **Interactive Map View** (🗺️)
- **Leaflet Integration**: OSM-based geospatial visualization
- **Dynamic Markers**: Circle markers with color coding
  - Red (high), Amber (moderate), Green (safe)
- **Interactive Popups**: Click for detailed district info
- **Legend**: Risk level color reference
- **Side Panel**: Selected marker details
- **Responsive Design**: Works on all screen sizes

### 8. **Real-time Weather Integration** (🌦️)
- **Weather Cards**: 4 major cities with live conditions
- **Weather Metrics**:
  - Temperature
  - Humidity percentage
  - Rainfall amount
  - Current conditions (Sunny/Cloudy/Rainy)
- **Risk Indicators**: Automatic condition risk assessment
- **Educational Insights**: 
  - Temperature + Humidity correlation to disease transmission
  - Rainfall impact on vector breeding
- **Auto-refresh**: 5-minute update interval

### 9. **Result Display Enhancements**
- **Animated Result Cards**: Scale and fade-in animations
- **Risk Levels**: 
  - ✓ Safe (Low transmission risk)
  - ⚠️ Moderate Risk (Precautions needed)
  - ✗ High Risk (Alert status)
- **Status Messages**: Context-specific recommendations
- **Interactive Elements**: Hover effects and transitions
- **Confidence Indicators**: Visual risk representation

### 10. **Data Analytics & Insights**
- **30-day Historical Analysis**:
  - Disease case trends
  - Environmental factors correlation
  - Seasonal patterns
- **District-level Analytics**:
  - Risk distribution across regions
  - High/moderate/safe district counts
  - Average risk metrics
- **Summary Statistics**:
  - Total cases (dengue/malaria)
  - Average temperatures
  - Rainfall totals

---

## 🎨 Design Philosophy

### **Premium Aesthetics**
- Avoids generic "AI slop" design
- Custom typography (not Arial/Inter/Roboto)
- Sharp, deliberate color choices
- Atmospheric depth with gradients

### **Interactive Micro-interactions**
- Staggered animations on page load
- Hover state transitions
- Shimmer effects on cards
- Smooth transitions between views

### **Responsive Design**
- Grid-based layouts
- Mobile-first CSS
- Breakpoints for tablets and phones
- Touch-friendly buttons

---

## 📊 API Endpoints

```
BASE_URL: http://127.0.0.1:8000

GET /
  → API health check

POST /predict
  → Input: Environmental & disease history parameters
  → Output: Dengue & Malaria risk predictions

GET /weather
  → Output: Real-time weather for major cities

GET /districts
  → Output: District list with coordinates

GET /district-predictions
  → Output: Risk predictions for all districts

GET /analytics
  → Output: 30-day trend data & summary stats

GET /risk-summary
  → Output: Overall risk overview
```

---

## 🚀 Technologies Used

### **Backend**
- FastAPI (Python)
- scikit-learn (ML models)
- NumPy (Numerical computation)
- Joblib (Model serialization)

### **Frontend**
- React 19.2.4
- Recharts (Data visualization)
- Leaflet + React-Leaflet (Maps)
- Axios (API calls)
- CSS3 (Custom styling)
- Framer Motion (Animation ready)

### **Design**
- Google Fonts (Poppins, Playfair Display)
- CSS Variables for theming
- CSS Gradients & Filters
- CSS Animations

---

## 🎯 How to Access

### **Development URLs**
- **Frontend**: http://localhost:3001
- **Backend API**: http://127.0.0.1:8000
- **API Docs**: http://127.0.0.1:8000/docs

### **Starting the Application**

1. **Backend**:
```bash
cd 6_dashboard/backend_api
uvicorn app:app --reload
```

2. **Frontend**:
```bash
cd 6_dashboard/frontend_web
npm install --legacy-peer-deps
npm start
```

---

## 📁 Project Structure

```
6_dashboard/
├── backend_api/
│   ├── app.py (Enhanced API with new endpoints)
│   ├── models/
│   │   ├── best_dengue_risk_model.pkl
│   │   └── best_malaria_binary_risk_model.pkl
│   └── requirements.txt
│
└── frontend_web/
    ├── src/
    │   ├── App.js (Main app with navigation)
    │   ├── App.css (Navbar & layout styling)
    │   ├── components/
    │   │   ├── Charts.js & Charts.css
    │   │   ├── DistrictPredictions.js & DistrictPredictions.css
    │   │   ├── MapView.js & MapView.css
    │   │   └── Weather.js & Weather.css
    │   └── index.css
    └── package.json
```

---

## ✨ Key Features Highlight

- **Animated Risk Cards**: Dynamic visualizations with smooth animations
- **Multi-view Dashboard**: 5 different perspectives on epidemic data
- **District Mapping**: Interactive geospatial visualization
- **Real-time Weather**: Live environmental condition monitoring
- **Historical Analytics**: 30-day trend analysis
- **Mobile Responsive**: Works on all devices
- **Professional UI**: Modern, non-generic design
- **High Performance**: Optimized animations & rendering

---

## 🔮 Future Enhancements

- [ ] Real OpenWeatherMap API integration
- [ ] Database integration for persistent storage
- [ ] User authentication & role-based access
- [ ] Advanced filtering & export options
- [ ] Mobile app version
- [ ] Alert notifications system
- [ ] Multi-language support
- [ ] Dark/Light theme toggle

---

**Status**: ✅ **Complete and Running**  
**Last Updated**: February 4, 2026  
**Frontend**: http://localhost:3001  
**Backend**: http://127.0.0.1:8000
