# 🏆 Scoresheet Halubilo - Team Building Score System

A modern, responsive web application built with Flask for managing team building activity scores. Track team performance, manage activities, and view real-time leaderboards with an intuitive interface.

## ✨ Features

### 🎯 Core Functionality
- **Team Management**: Create, edit, and delete teams with custom colors
- **Activity Management**: Define team building activities with maximum scores
- **User Management**: Create user accounts assigned to specific activities for activity heads
- **Score Entry**: Easy score input with team and activity selection
- **Real-time Leaderboard**: Live ranking based on total scores
- **Comprehensive Dashboard**: Performance analytics and statistics

### 🎨 User Interface
- **Modern Design**: Clean, responsive interface using Tailwind CSS
- **Mobile Friendly**: Works seamlessly on all devices
- **Interactive Elements**: Hover effects, animations, and smooth transitions
- **Color-coded Teams**: Visual team identification with custom colors
- **Intuitive Navigation**: Easy-to-use navigation between sections

### 📊 Analytics & Reporting
- **Performance Metrics**: Total scores, averages, and rankings
- **Activity Statistics**: Usage tracking and performance analysis
- **Team Insights**: Best performers, most active teams
- **Historical Data**: Track scores over time with timestamps

## 🚀 Quick Start

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)

### Installation

1. **Clone or download the project**
   ```bash
   # If using git
   git clone <repository-url>
   cd scoresheet-halubilo
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python app.py
   ```

4. **Open your browser**
   Navigate to `http://localhost:5000`

### First Time Setup

1. **Add Teams**: Go to Teams section and create your first teams
2. **Create Activities**: Define team building activities with maximum scores
3. **Enter Scores**: Start recording team performance in the Scores section
4. **View Dashboard**: Monitor performance and rankings in real-time

## 🏗️ Project Structure

```
scoresheet-halubilo/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── templates/            # HTML templates
│   ├── base.html         # Base template with navigation
│   ├── index.html        # Home page with leaderboard
│   ├── teams.html        # Team management
│   ├── activities.html   # Activity management
│   ├── scores.html       # Score entry and management
│   ├── dashboard.html    # Analytics dashboard
│   ├── edit_team.html    # Edit team form
│   ├── edit_activity.html # Edit activity form
│   └── edit_score.html   # Edit score form
└── scoresheet.db         # SQLite database (created automatically)
```

## 🎮 Usage Guide

### Managing Teams
- **Add Team**: Enter team name and select a color
- **Edit Team**: Modify team information or change colors
- **Delete Team**: Remove teams (with confirmation)

### Managing Activities
- **Create Activity**: Define name, description, and maximum score
- **Edit Activity**: Update activity details
- **Delete Activity**: Remove activities (with confirmation)
- **Quick User Creation**: Create user accounts for activity participants during activity setup

### Recording Scores
- **Select Team**: Choose from available teams
- **Select Activity**: Pick the team building activity
- **Enter Score**: Input the team's score (0 to max)
- **Add Notes**: Optional comments or observations
- **Submit**: Save the score to the system

### Viewing Results
- **Home Page**: Quick overview with current leaderboard
- **Dashboard**: Detailed performance analytics
- **Scores Page**: Complete score history and management

## 🔧 Configuration

### Environment Variables
The application uses default configurations, but you can customize:

- **Database**: SQLite database (configurable in `app.py`)
- **Secret Key**: Change the secret key for production use
- **Port**: Default port 5000 (configurable)

### Database
- **Type**: SQLite (lightweight, no setup required)
- **Location**: `scoresheet.db` in the project root
- **Auto-creation**: Database and tables are created automatically

## 🚀 Deployment

### Local Development
```bash
python app.py
```

### Production Deployment
1. **Set Environment Variables**
   ```bash
   export FLASK_ENV=production
   export SECRET_KEY=your-secure-secret-key
   ```

2. **Use Production WSGI Server**
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

3. **Reverse Proxy** (Optional)
   - Configure Nginx or Apache as reverse proxy
   - Enable HTTPS with SSL certificates

## 🛠️ Customization

### Styling
- **Colors**: Modify primary colors in `templates/base.html`
- **Layout**: Adjust Tailwind CSS classes for different layouts
- **Themes**: Create custom themes by modifying CSS variables

### Features
- **Scoring System**: Modify score validation and calculation logic
- **Team Categories**: Add team divisions or categories
- **Activity Types**: Implement different activity scoring methods
- **Export**: Add CSV/PDF export functionality

## 🔒 Security Features

- **CSRF Protection**: Built-in Flask-WTF CSRF tokens
- **Input Validation**: Form validation and sanitization
- **SQL Injection Protection**: SQLAlchemy ORM protection
- **XSS Prevention**: Template auto-escaping

## 📱 Browser Support

- **Modern Browsers**: Chrome, Firefox, Safari, Edge
- **Mobile**: Responsive design for all screen sizes
- **JavaScript**: Required for interactive features

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

### Common Issues

**Database Errors**
- Ensure you have write permissions in the project directory
- Delete `scoresheet.db` to reset the database

**Port Already in Use**
- Change the port in `app.py` or kill the process using port 5000

**Template Errors**
- Verify all template files are in the `templates/` directory
- Check for proper Jinja2 syntax

### Getting Help
- Check the console for error messages
- Verify all dependencies are installed
- Ensure Python version compatibility

## 🎉 Acknowledgments

- **Flask**: Web framework
- **SQLAlchemy**: Database ORM
- **Tailwind CSS**: Styling framework
- **WTForms**: Form handling and validation

---

**Built with ❤️ for team building success!**
