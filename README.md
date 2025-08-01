# 🏆 GitHub Leaderboard Mini App Pro

## Ultimate Enhanced Version - Enterprise-Grade Features

A next-generation developer community platform with real-time analytics, AI-powered insights, and mobile-first PWA capabilities.

![Status](https://img.shields.io/badge/Status-Ultimate%20Pro-gold)
![Python](https://img.shields.io/badge/Python-3.8+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-Latest-red)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13+-blue)
![PWA](https://img.shields.io/badge/PWA-Enabled-green)
![Security](https://img.shields.io/badge/Security-Enterprise-orange)

## ✨ Features

### 🎨 Modern UI/UX
- **Glassmorphism Design**: Beautiful translucent cards with backdrop blur effects
- **Gradient Themes**: Eye-catching color gradients throughout the interface
- **Responsive Layout**: Optimized for desktop, tablet, and mobile devices
- **Interactive Charts**: Dynamic visualizations using Plotly
- **Smooth Animations**: Hover effects and transitions for better user experience

### 📊 Advanced Analytics
- **User Contribution Charts**: Pie charts showing contribution distribution
- **Leaderboard Visualizations**: Horizontal bar charts for top performers
- **Activity Timeline**: Track community activity over time
- **Personal Dashboard**: Detailed user profile with GitHub integration
- **Real-time Statistics**: Live updates of community metrics

### 🏅 Achievement System
- **PR Master**: For users with 50+ merged pull requests
- **Bug Hunter**: For users who closed 25+ issues
- **Code Warrior**: For users with 1000+ commits
- **Star Gazer**: For users who starred 100+ repositories
- **Open Source Hero**: For users contributing to 20+ repositories

### 🔄 Background Processing
- **Automatic Score Updates**: Scheduled updates every 6 hours
- **Rate Limit Handling**: Smart API request management
- **Error Resilience**: Robust error handling and retry mechanisms

### 🔐 Enhanced Security
- **Password Hashing**: Secure password storage using Werkzeug
- **Session Management**: Proper user session handling
- **Environment Variables**: Secure configuration management

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- PostgreSQL 13+
- GitHub API Token (optional, for higher rate limits)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/github-leaderboard.git
cd github-leaderboard
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**
Create a `.env` file in the root directory:
```env
DB_NAME=leaderboard
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
GITHUB_TOKEN=your_github_token  # Optional but recommended
```

4. **Set up PostgreSQL database**
```sql
CREATE DATABASE leaderboard;
```

5. **Run the application**
```bash
# Modern version with enhanced features
streamlit run app_modern.py

# Or the original version
streamlit run app_postgresql.py
```

6. **Access the application**
Open your browser and navigate to `http://localhost:8501`

## 📁 Project Structure

```
github-leaderboard/
├── app_modern.py              # Enhanced main application
├── app_postgresql.py          # Original application
├── requirements.txt           # Python dependencies
├── .env                      # Environment variables (create this)
├── styles/
│   └── modern_ui.py          # Custom CSS and UI components
├── components/
│   └── dashboard.py          # Dashboard and chart components
├── utils/
│   └── background_tasks.py   # Background processing
├── config/
│   └── settings.py           # Configuration settings
├── backend/                  # Original backend files
│   ├── services.py
│   ├── app.py
│   ├── main.py
│   └── ...
└── README.md
```

## 🎯 Usage

### For Users
1. **Sign Up**: Create an account using your GitHub profile URL
2. **Login**: Access your personalized dashboard
3. **View Profile**: Check your detailed statistics and achievements
4. **Leaderboard**: Compare your performance with other users
5. **Auto-Updates**: Scores update automatically every 6 hours

### For Administrators
- Monitor database through PostgreSQL admin tools
- Configure update intervals in `config/settings.py`
- Start background scheduler: `python utils/background_tasks.py`

## 📊 Scoring System

The application calculates scores based on GitHub activities:

| Activity | Weight | Description |
|----------|--------|-------------|
| Pull Requests Opened | 2 | Points for creating PRs |
| Pull Requests Merged | 5 | Points for successful contributions |
| Issues Created | 1 | Points for reporting issues |
| Issues Closed | 3 | Points for resolving issues |
| Repositories | 2 | Points per repository contributed to |
| Stars Given | 0.5 | Points for starring repositories |
| Commits | 0.1 | Points per commit |

## 🔧 Configuration

Customize the application behavior in `config/settings.py`:

- **Themes**: Modify colors and styling
- **Scoring**: Adjust point weights and achievement thresholds
- **Features**: Enable/disable specific functionality
- **Performance**: Configure rate limits and batch sizes

## 🆕 New Features vs Original

| Feature | Original | Modern Version |
|---------|----------|----------------|
| UI Design | Basic Streamlit | Glassmorphism + Gradients |
| Charts | Simple tables | Interactive Plotly charts |
| User Profiles | Basic info | Rich profiles with avatars |
| Achievements | None | Badge system |
| Real-time Updates | Manual | Automatic background tasks |
| Mobile Support | Limited | Fully responsive |
| Analytics | Basic stats | Advanced visualizations |
| Performance | Single queries | Optimized batch processing |

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Streamlit](https://streamlit.io/) for the amazing framework
- [Plotly](https://plotly.com/) for beautiful visualizations
- [GitHub API](https://docs.github.com/en/rest) for providing the data
- [PostgreSQL](https://www.postgresql.org/) for reliable data storage

## 📞 Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/yourusername/github-leaderboard/issues) page
2. Create a new issue with detailed information
3. Join our [Discussions](https://github.com/yourusername/github-leaderboard/discussions)

## 🗺️ Roadmap

- [ ] Team/Organization support
- [ ] Export functionality (CSV, PDF)
- [ ] Email notifications
- [ ] Dark mode toggle
- [ ] Advanced filtering and search
- [ ] GitHub Actions integration
- [ ] Mobile app version

---

**Built with ❤️ by the community**
