# Enhanced Information Validation Tool

🚀 **Automated validation for Site Survey and Install Plan documents with n8n-inspired UI**

[![Docker](https://img.shields.io/badge/Docker-Ready-blue?logo=docker)](https://www.docker.com/)
[![React](https://img.shields.io/badge/React-18+-61DAFB?logo=react)](https://reactjs.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0+-000000?logo=flask)](https://flask.palletsprojects.com/)
[![Google APIs](https://img.shields.io/badge/Google-APIs-4285F4?logo=google)](https://developers.google.com/)

## 🎯 Overview

The Enhanced Information Validation Tool is a comprehensive solution for validating Site Survey and Install Plan documents. It features a modern n8n-inspired user interface with dark theme, professional numbered navigation tabs, and real-time validation processing.

### ✨ Key Features

- **🔍 Comprehensive Validation**: 50+ validation criteria across 8 categories
- **📊 Real-time Analytics**: Performance metrics and trend analysis
- **🔗 Google Integration**: Direct processing from Google Sheets and Drive
- **🎨 Professional UI**: n8n-inspired design with dark theme
- **📈 Advanced Analytics**: Category performance and issue tracking
- **📤 Export Capabilities**: PDF, Excel, and CSV export options
- **🐳 Docker Ready**: Complete containerization for easy deployment

## 🏗️ Architecture

```
ps-doc-analysis/
├── validation_tool/          # Backend Flask API
│   ├── src/                  # Source code
│   ├── Dockerfile           # Backend container
│   └── requirements.txt     # Python dependencies
├── validation-dashboard/     # Frontend React App
│   ├── src/                 # React components
│   ├── public/              # Static assets
│   ├── Dockerfile          # Frontend container
│   └── package.json        # Node dependencies
├── docker-compose.yml       # Multi-container orchestration
├── Makefile                # Convenient Docker commands
└── README.md               # This file
```

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Git
- Google Cloud Service Account (for Google APIs)

### 1. Clone the Repository

```bash
git clone https://github.com/rstamps01/ps-doc-analysis.git
cd ps-doc-analysis
```

### 2. Environment Setup

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your configuration
nano .env
```

### 3. Start the Application

```bash
# Build and start all services
make build
make up

# Or use Docker Compose directly
docker-compose up -d
```

### 4. Access the Application

- **Frontend**: http://localhost
- **Backend API**: http://localhost:5001
- **Health Check**: http://localhost:5001/health

## 🔧 Configuration

### Google API Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Google Sheets API and Google Drive API
4. Create a service account with appropriate permissions
5. Download the JSON key file
6. Mount the credentials file to `/app/credentials/google-service-account.json`

### Environment Variables

Key configuration options in `.env`:

```bash
# Application
FLASK_ENV=production
PORT=5001

# Google APIs
GOOGLE_APPLICATION_CREDENTIALS=/app/credentials/google-service-account.json

# Database
DATABASE_URL=sqlite:///data/validation_tool.db

# Security
SECRET_KEY=your_secret_key_here
```

## 🐳 Docker Commands

Use the included Makefile for convenient operations:

```bash
make build     # Build all images
make up        # Start services
make down      # Stop services
make logs      # View logs
make health    # Check service health
make clean     # Clean up resources
```

## 📊 Validation Process

### Document Types Supported

1. **Site Survey Part 1**: Project details and technical specifications
2. **Site Survey Part 2**: Network diagrams and infrastructure requirements
3. **Install Plan**: Installation procedures and commissioning checklist
4. **Evaluation Criteria**: Validation rules and thresholds

### Validation Categories

- **Document Completeness** (25% weight)
- **Technical Requirements** (25% weight)
- **SFDC Integration** (25% weight)
- **Cross-Document Consistency** (25% weight)

### Scoring System

- **Pass**: ≥80% score (configurable)
- **Warning**: 60-79% score (configurable)
- **Fail**: <60% score

## 🎨 User Interface

### n8n-Inspired Design Features

- **Numbered Navigation Tabs**: Professional 1-5 tab system
- **Dark Theme**: Modern professional appearance
- **Card-Based Layout**: Clean visual hierarchy
- **Real-time Updates**: Live validation progress
- **Responsive Design**: Mobile and desktop friendly

### Main Sections

1. **Dashboard**: Overview and active validation runs
2. **Validation**: Document configuration and processing
3. **Analytics**: Performance metrics and trends
4. **Export**: Report generation and download
5. **Settings**: API configuration and system settings

## 📈 Analytics & Reporting

### Performance Metrics

- Overall validation scores and trends
- Category performance breakdown
- Common issues identification
- Processing time analysis

### Export Options

- **PDF Reports**: Executive summaries with charts
- **Excel Workbooks**: Detailed data with pivot tables
- **CSV Data**: Raw data for custom analysis

## 🔍 API Documentation

### Health Check

```bash
GET /health
```

### Validation Endpoints

```bash
POST /api/validation/comprehensive
GET /api/real-data/dashboard-stats
GET /api/real-data/validation-history
```

### Google Integration

```bash
POST /api/google/sheets/process
POST /api/google/drive/process
```

## 🛠️ Development

### Local Development Setup

```bash
# Backend development
cd validation_tool
pip install -r requirements.txt
python src/main.py

# Frontend development
cd validation-dashboard
npm install
npm run dev
```

### Building Custom Images

```bash
# Backend only
docker build -t validation-tool-backend ./validation_tool

# Frontend only
docker build -t validation-tool-frontend ./validation-dashboard
```

## 🔒 Security

- CORS configuration for cross-origin requests
- Environment variable management
- Secure credential handling
- Input validation and sanitization

## 📋 Testing

### Health Checks

```bash
# Test all services
make test

# Manual health checks
curl http://localhost:5001/health
curl http://localhost/health
```

### Validation Testing

Use the included test documents:
- Site Survey Part 1: Google Sheets URL
- Site Survey Part 2: Google Sheets URL
- Install Plan: Google Drive PDF URL

## 🚀 Deployment

### Production Deployment

1. **Environment Setup**: Configure production environment variables
2. **SSL/TLS**: Set up reverse proxy with SSL certificates
3. **Monitoring**: Implement logging and monitoring solutions
4. **Scaling**: Use Docker Swarm or Kubernetes for scaling

### Cloud Deployment Options

- **AWS**: ECS, EKS, or EC2 with Docker
- **Google Cloud**: Cloud Run, GKE, or Compute Engine
- **Azure**: Container Instances, AKS, or Virtual Machines
- **DigitalOcean**: App Platform or Droplets

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

### Common Issues

1. **Docker Permission Errors**: Add user to docker group
2. **Google API Errors**: Check service account permissions
3. **Build Failures**: Ensure all required files are present

### Getting Help

- Check the logs: `make logs`
- Verify health: `make health`
- Review configuration: Check `.env` file

## 🎉 Acknowledgments

- Inspired by n8n's professional interface design
- Built with modern React and Flask technologies
- Powered by Google APIs for document processing

---

**Made with ❤️ for automated document validation**

