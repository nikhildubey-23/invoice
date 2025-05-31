# Repair Center Management System

A comprehensive web application for managing a device repair center, built with Flask and SQLite.

## Features

- Customer Management
- Device Tracking
- Service Ticket System
- Invoice Generation
- PDF Report Generation
- User Authentication
- Role-based Access Control

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Git (optional, for cloning the repository)

## Installation

1. Clone the repository or download the source code:
```bash
git clone <repository-url>
cd repair_center
```

2. Create a virtual environment (recommended):
```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

4. Initialize the database:
```bash
python init_db.py
```

## Project Structure

```
repair_center/
├── app.py              # Main application file
├── init_db.py          # Database initialization script
├── requirements.txt    # Python dependencies
├── repair_center.db    # SQLite database file
├── invoices/          # Directory for generated PDF invoices
├── static/            # Static files (CSS, JS, images)
└── templates/         # HTML templates
```

## Configuration

1. Set up environment variables (optional):
```bash
# On Windows
set FLASK_APP=app.py
set FLASK_ENV=development

# On macOS/Linux
export FLASK_APP=app.py
export FLASK_ENV=development
```

2. Update the secret key in `app.py`:
```python
app.config['SECRET_KEY'] = 'your-secure-secret-key-here'
```

## Running the Application

1. Start the Flask development server:
```bash
python app.py
```

2. Open your web browser and navigate to:
```
http://localhost:5000
```

## Default Login

- Username: admin
- Password: admin123

**Note:** Change the default credentials after first login for security.

## Usage

1. **Customer Management**
   - Add new customers
   - View customer list
   - Edit customer details
   - Delete customers

2. **Device Management**
   - Register new devices
   - Track device status
   - Update device information
   - View device history

3. **Service Tickets**
   - Create new service tickets
   - Assign technicians
   - Update ticket status
   - Add service details

4. **Invoicing**
   - Generate invoices
   - Download PDF invoices
   - Track payment status
   - Apply discounts and taxes

## Troubleshooting

1. **Database Issues**
   - Delete `repair_center.db` if corrupted
   - Run `python init_db.py` to recreate the database

2. **PDF Generation Issues**
   - Ensure the `invoices` directory exists
   - Check write permissions in the project directory

3. **Module Not Found Errors**
   - Verify virtual environment is activated
   - Run `pip install -r requirements.txt` again

## Security Notes

1. Change the default secret key in production
2. Use strong passwords for all user accounts
3. Regularly backup the database file
4. Keep all dependencies updated

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please open an issue in the repository or contact the development team. 