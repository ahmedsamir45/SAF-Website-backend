# Student Activity Platform (SAF) - Backend

[![GitHub stars](https://img.shields.io/github/stars/ahmedsamir45/SAF-Website-backend?style=social)](https://github.com/ahmedsamir45/SAF-Website-backend/stargazers)
[![GitHub issues](https://img.shields.io/github/issues/ahmedsamir45/SAF-Website-backend)](https://github.com/ahmedsamir45/SAF-Website-backend/issues)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A comprehensive backend system for managing student activities, programs, and user interactions at the Faculty of Science, Helwan University. Built with Django REST Framework and PostgreSQL, this platform serves as the backbone for the Student Activity Website, enabling seamless management of academic programs, events, and student engagement.

## ✨ Features

- **User Authentication** - JWT-based authentication system
- **Program Management** - Create, read, update, and delete programs
- **Favorites System** - Users can save favorite programs
- **Contact Form** - Integrated email notification system
- **Admin Dashboard** - Full-featured admin interface
- **RESTful API** - Well-documented API endpoints
- **File Uploads** - Support for program images and media

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- PostgreSQL
- Node.js & npm (for frontend)
- pip (Python package manager)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/ahmedsamir45/SAF-Website-backend.git
   cd SAF-Website-backend
   ```

2. **Set up a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the root directory with the following variables:
   ```env
   SECRET_KEY=your-secret-key
   DEBUG=True
   DATABASE_URL=postgres://user:password@localhost:5432/saf_db
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=your-app-password
   DEFAULT_FROM_EMAIL=your-email@gmail.com
   ADMIN_EMAIL=admin@example.com
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create a superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run the development server**
   ```bash
   python manage.py runserver
   ```

## 🛠️ API Endpoints

### Authentication
- `POST /api/auth/jwt/create/` - Obtain JWT token
- `POST /api/auth/users/` - Register new user
- `GET /api/auth/users/me/` - Get current user profile

### Programs
- `GET /api/programs/` - List all programs
- `POST /api/programs/` - Create new program (Admin only)
- `GET /api/programs/{id}/` - Get program details
- `PUT /api/programs/{id}/` - Update program (Admin only)

### Favorites
- `GET /api/programs/favorites/` - Get user's favorite programs
- `POST /api/programs/{id}/favorite/` - Toggle favorite status

### Contact
- `POST /api/contact/` - Submit contact form

## 📝 Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `SECRET_KEY` | Django secret key | Yes | - |
| `DEBUG` | Debug mode | No | False |
| `DATABASE_URL` | Database connection URL | Yes | - |
| `EMAIL_HOST` | SMTP server host | No | - |
| `EMAIL_PORT` | SMTP server port | No | 587 |
| `EMAIL_USE_TLS` | Use TLS for email | No | True |
| `EMAIL_HOST_USER` | Email username | No | - |
| `EMAIL_HOST_PASSWORD` | Email password | No | - |
| `DEFAULT_FROM_EMAIL` | Default sender email | No | - |
| `ADMIN_EMAIL` | Admin email for notifications | No | - |

## 🧪 Testing

Run the test suite with:
```bash
python manage.py test
```

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📧 Contact

For any questions or feedback, please contact [ahmedsamer6788@gmail.com](mailto:ahmedsamer6788@gmail.com)
