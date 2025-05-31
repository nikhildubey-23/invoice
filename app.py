from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime
import os
from werkzeug.security import generate_password_hash, check_password_hash
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, HRFlowable, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT

# Add Rupee symbol constant
RUPEE_SYMBOL = '₹'

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'  # Change this to a secure secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///repair_center.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    role = db.Column(db.String(20), nullable=False, default='technician')

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    address = db.Column(db.String(200))
    devices = db.relationship('Device', backref='customer', lazy=True)

class Device(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    brand = db.Column(db.String(50), nullable=False)
    model = db.Column(db.String(50), nullable=False)
    serial_number = db.Column(db.String(50))
    issue = db.Column(db.Text)
    tickets = db.relationship('Ticket', backref='device', lazy=True)

class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey('device.id'), nullable=False)
    technician_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='Received')
    created_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    services = db.relationship('Service', backref='ticket', lazy=True)
    invoice = db.relationship('Invoice', backref='ticket', uselist=False)
    technician = db.relationship('User', backref='tickets')

class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey('ticket.id'), nullable=False)
    description = db.Column(db.Text, nullable=False)
    cost = db.Column(db.Float, nullable=False)

class Invoice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey('ticket.id'), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    paid_status = db.Column(db.String(20), nullable=False, default='Unpaid')
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    tax_rate = db.Column(db.Float, default=0)
    discount = db.Column(db.Float, default=0)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Get summary statistics
    total_customers = Customer.query.count()
    total_devices = Device.query.count()
    total_tickets = Ticket.query.count()
    completed_tickets = Ticket.query.filter_by(status='Completed').count()
    total_invoices = Invoice.query.count()
    
    # Calculate total revenue
    total_revenue = db.session.query(db.func.sum(Invoice.total_amount)).scalar() or 0
    
    return render_template('dashboard.html',
                         total_customers=total_customers,
                         total_devices=total_devices,
                         total_tickets=total_tickets,
                         completed_tickets=completed_tickets,
                         total_invoices=total_invoices,
                         total_revenue=total_revenue)

# Customer routes
@app.route('/customers')
@login_required
def customers():
    customers = Customer.query.all()
    return render_template('customers.html', customers=customers)

@app.route('/customers/add', methods=['GET', 'POST'])
@login_required
def add_customer():
    if request.method == 'POST':
        customer = Customer(
            name=request.form['name'],
            phone=request.form['phone'],
            email=request.form['email'],
            address=request.form['address']
        )
        db.session.add(customer)
        db.session.commit()
        flash('Customer added successfully')
        return redirect(url_for('customers'))
    return render_template('add_customer.html')

@app.route('/customers/<int:customer_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_customer(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    if request.method == 'POST':
        customer.name = request.form['name']
        customer.email = request.form['email']
        customer.phone = request.form['phone']
        customer.address = request.form['address']
        db.session.commit()
        flash('Customer updated successfully!', 'success')
        return redirect(url_for('customers'))
    return render_template('edit_customer.html', customer=customer)

@app.route('/customers/<int:customer_id>/delete', methods=['POST'])
@login_required
def delete_customer(customer_id):
    try:
        customer = Customer.query.get_or_404(customer_id)
        
        # First delete all related services
        for device in customer.devices:
            for ticket in device.tickets:
                Service.query.filter_by(ticket_id=ticket.id).delete()
                Invoice.query.filter_by(ticket_id=ticket.id).delete()
                Ticket.query.filter_by(id=ticket.id).delete()
        
        # Then delete all devices
        Device.query.filter_by(customer_id=customer_id).delete()
        
        # Finally delete the customer
        db.session.delete(customer)
        db.session.commit()
        flash('Customer and all related records deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting customer. Please try again.', 'error')
        print(f"Error deleting customer: {str(e)}")
    
    return redirect(url_for('customers'))

# Device routes
@app.route('/devices')
@login_required
def devices():
    devices = Device.query.all()
    return render_template('devices.html', devices=devices)

@app.route('/devices/add', methods=['GET', 'POST'])
@login_required
def add_device():
    if request.method == 'POST':
        device = Device(
            customer_id=request.form['customer_id'],
            brand=request.form['brand'],
            model=request.form['model'],
            serial_number=request.form['serial_number'],
            issue=request.form['issue']
        )
        db.session.add(device)
        db.session.commit()
        flash('Device added successfully')
        return redirect(url_for('devices'))
    customers = Customer.query.all()
    return render_template('add_device.html', customers=customers)

@app.route('/devices/<int:device_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_device(device_id):
    device = Device.query.get_or_404(device_id)
    if request.method == 'POST':
        # Validate customer_id
        customer_id = request.form.get('customer_id')
        if not customer_id:
            flash('Customer is required', 'error')
            return redirect(url_for('edit_device', device_id=device_id))
            
        device.customer_id = customer_id
        device.brand = request.form['brand']
        device.model = request.form['model']
        device.serial_number = request.form['serial_number']
        device.issue = request.form['issue']
        
        try:
            db.session.commit()
            flash('Device updated successfully!', 'success')
            return redirect(url_for('devices'))
        except Exception as e:
            db.session.rollback()
            flash('Error updating device. Please try again.', 'error')
            return redirect(url_for('edit_device', device_id=device_id))
            
    customers = Customer.query.all()
    return render_template('edit_device.html', device=device, customers=customers)

@app.route('/devices/<int:device_id>/delete', methods=['POST'])
@login_required
def delete_device(device_id):
    device = Device.query.get_or_404(device_id)
    db.session.delete(device)
    db.session.commit()
    flash('Device deleted successfully!', 'success')
    return redirect(url_for('devices'))

# Ticket routes
@app.route('/tickets')
@login_required
def tickets():
    tickets = Ticket.query.all()
    return render_template('tickets.html', tickets=tickets)

@app.route('/tickets/add', methods=['GET', 'POST'])
@login_required
def add_ticket():
    if request.method == 'POST':
        ticket = Ticket(
            device_id=request.form['device_id'],
            technician_id=current_user.id,
            status=request.form['status']
        )
        db.session.add(ticket)
        db.session.commit()
        flash('Ticket created successfully')
        return redirect(url_for('tickets'))
    devices = Device.query.all()
    return render_template('add_ticket.html', devices=devices)

@app.route('/tickets/<int:ticket_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_ticket(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    if request.method == 'POST':
        ticket.status = request.form['status']
        db.session.commit()
        flash('Ticket updated successfully!', 'success')
        return redirect(url_for('tickets'))
    return render_template('edit_ticket.html', ticket=ticket)

@app.route('/tickets/<int:ticket_id>/delete', methods=['POST'])
@login_required
def delete_ticket(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    db.session.delete(ticket)
    db.session.commit()
    flash('Ticket deleted successfully!', 'success')
    return redirect(url_for('tickets'))

# Service routes
@app.route('/services')
@login_required
def services():
    services = Service.query.all()
    print("Services:", [(s.id, s.description) for s in services])  # Debug print
    return render_template('services.html', services=services)

@app.route('/services/add', methods=['GET', 'POST'])
@login_required
def add_service():
    if request.method == 'POST':
        service = Service(
            ticket_id=request.form['ticket_id'],
            description=request.form['description'],
            cost=float(request.form['cost'])
        )
        db.session.add(service)
        db.session.commit()
        flash('Service added successfully')
        return redirect(url_for('services'))
    tickets = Ticket.query.filter_by(status='Completed').all()
    return render_template('add_service.html', tickets=tickets)

@app.route('/services/<int:service_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_service(service_id):
    service = Service.query.get_or_404(service_id)
    if request.method == 'POST':
        service.description = request.form['description']
        service.cost = float(request.form['cost'])
        db.session.commit()
        flash('Service updated successfully!', 'success')
        return redirect(url_for('services'))
    return render_template('edit_service.html', service=service)

@app.route('/services/<int:service_id>/delete', methods=['POST'])
@login_required
def delete_service(service_id):
    service = Service.query.get_or_404(service_id)
    db.session.delete(service)
    db.session.commit()
    flash('Service deleted successfully!', 'success')
    return redirect(url_for('services'))

# Invoice routes
@app.route('/invoices')
@login_required
def invoices():
    invoices = Invoice.query.all()
    return render_template('invoices.html', invoices=invoices)

@app.route('/invoices/generate', methods=['GET', 'POST'])
@login_required
def generate_invoice():
    if request.method == 'POST':
        ticket_id = request.form['ticket_id']
        ticket = Ticket.query.get_or_404(ticket_id)
        
        # Calculate total from services
        total_amount = sum(service.cost for service in ticket.services)
        tax_rate = float(request.form['tax_rate'])
        discount = float(request.form['discount'])
        
        # Calculate final total
        tax_amount = total_amount * (tax_rate / 100)
        final_total = total_amount + tax_amount - discount
        
        invoice = Invoice(
            ticket_id=ticket_id,
            total_amount=final_total,
            paid_status=request.form['paid_status'],
            tax_rate=tax_rate,
            discount=discount
        )
        db.session.add(invoice)
        db.session.commit()
        
        # Generate PDF
        generate_invoice_pdf(invoice.id)
        
        flash('Invoice generated successfully')
        return redirect(url_for('invoices'))
    
    tickets = Ticket.query.filter_by(status='Completed').all()
    return render_template('generate_invoice.html', tickets=tickets)

@app.route('/invoices/<int:invoice_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_invoice(invoice_id):
    invoice = Invoice.query.get_or_404(invoice_id)
    if request.method == 'POST':
        invoice.paid_status = request.form['paid_status']
        invoice.tax_rate = float(request.form['tax_rate'])
        invoice.discount = float(request.form['discount'])
        
        # Recalculate total amount
        total_amount = sum(service.cost for service in invoice.ticket.services)
        tax_amount = total_amount * (invoice.tax_rate / 100)
        invoice.total_amount = total_amount + tax_amount - invoice.discount
        
        db.session.commit()
        flash('Invoice updated successfully!', 'success')
        return redirect(url_for('invoices'))
    return render_template('edit_invoice.html', invoice=invoice)

@app.route('/invoices/<int:invoice_id>/delete', methods=['POST'])
@login_required
def delete_invoice(invoice_id):
    invoice = Invoice.query.get_or_404(invoice_id)
    db.session.delete(invoice)
    db.session.commit()
    flash('Invoice deleted successfully!', 'success')
    return redirect(url_for('invoices'))

def generate_invoice_pdf(invoice_id):
    invoice = Invoice.query.get_or_404(invoice_id)
    ticket = invoice.ticket
    device = ticket.device
    customer = device.customer
    
    # Create PDF file
    pdf_file = f"invoices/invoice_{invoice_id}.pdf"
    doc = SimpleDocTemplate(pdf_file, pagesize=letter)
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        alignment=TA_CENTER,
        spaceAfter=30,
        fontSize=24,
        textColor=colors.HexColor('#2c3e50')
    )
    
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Heading2'],
        alignment=TA_CENTER,
        spaceAfter=20,
        fontSize=16,
        textColor=colors.HexColor('#34495e')
    )
    
    info_style = ParagraphStyle(
        'Info',
        parent=styles['Normal'],
        spaceAfter=12,
        fontSize=12,
        textColor=colors.HexColor('#2c3e50')
    )
    
    # Add company header
    elements.append(Paragraph("Repair Center", title_style))
    elements.append(Paragraph("Professional Device Repair Services", subtitle_style))
    
    # Add horizontal line
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#bdc3c7'), spaceBefore=10, spaceAfter=20))
    
    # Create two columns for invoice info and customer details
    invoice_info = [
        Paragraph(f"<b>Invoice #:</b> {invoice_id}", info_style),
        Paragraph(f"<b>Date:</b> {invoice.date.strftime('%B %d, %Y')}", info_style),
        Paragraph(f"<b>Status:</b> {invoice.paid_status}", info_style)
    ]
    
    # Create customer info with proper indentation and spacing
    customer_info = [
        Paragraph("<b>Bill To:</b>", info_style),
        Paragraph(f"<b>{customer.name}</b>", info_style),
        Paragraph(f"<br/>&nbsp;&nbsp;&nbsp;&nbsp;{customer.address}", info_style),
        Paragraph(f"<br/>&nbsp;&nbsp;&nbsp;&nbsp;Phone: {customer.phone}", info_style),
        Paragraph(f"<br/>&nbsp;&nbsp;&nbsp;&nbsp;Email: {customer.email}", info_style)
    ]
    
    # Create two column layout with adjusted widths
    col1_width = 200
    col2_width = 300
    col1 = [Paragraph(p.text, p.style) for p in invoice_info]
    col2 = [Paragraph(p.text, p.style) for p in customer_info]
    
    # Add columns to document with proper spacing
    elements.append(Table([[col1, col2]], colWidths=[col1_width, col2_width], style=[
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(Spacer(1, 20))
    
    # Add device information
    elements.append(Paragraph("<b>Device Information:</b>", info_style))
    device_info = [
        f"Brand: {device.brand}",
        f"Model: {device.model}",
        f"Serial Number: {device.serial_number}",
        f"Issue: {device.issue}"
    ]
    for info in device_info:
        elements.append(Paragraph(info, info_style))
    
    elements.append(Spacer(1, 20))
    
    # Add services table with fancy styling
    services_data = [['Description', 'Cost']]
    subtotal = 0
    for service in ticket.services:
        services_data.append([service.description, f"{RUPEE_SYMBOL} {service.cost:.2f}"])
        subtotal += service.cost
    
    # Calculate tax and total
    tax_amount = subtotal * (invoice.tax_rate / 100)
    final_total = subtotal + tax_amount - invoice.discount
    
    # Add summary rows
    services_data.append(['', ''])  # Empty row for spacing
    services_data.append(['Subtotal', f"{RUPEE_SYMBOL} {subtotal:.2f}"])
    services_data.append(['Tax', f"{RUPEE_SYMBOL} {tax_amount:.2f}"])
    services_data.append(['Discount', f"-{RUPEE_SYMBOL} {invoice.discount:.2f}"])
    services_data.append(['Total', f"{RUPEE_SYMBOL} {final_total:.2f}"])
    
    # Create table with fancy styling
    table = Table(services_data, colWidths=[400, 100])
    table.setStyle(TableStyle([
        # Header styling
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        
        # Body styling
        ('BACKGROUND', (0, 1), (-1, -5), colors.white),
        ('TEXTCOLOR', (0, 1), (-1, -5), colors.HexColor('#2c3e50')),
        ('ALIGN', (0, 1), (-1, -5), 'LEFT'),
        ('FONTNAME', (0, 1), (-1, -5), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -5), 10),
        ('GRID', (0, 0), (-1, -5), 1, colors.HexColor('#bdc3c7')),
        
        # Summary section styling
        ('BACKGROUND', (0, -4), (-1, -1), colors.HexColor('#f8f9fa')),
        ('TEXTCOLOR', (0, -4), (-1, -1), colors.HexColor('#2c3e50')),
        ('ALIGN', (0, -4), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, -4), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, -4), (-1, -1), 10),
        ('GRID', (0, -4), (-1, -1), 1, colors.HexColor('#bdc3c7')),
        
        # Total row styling
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#2ecc71')),
        ('TEXTCOLOR', (0, -1), (-1, -1), colors.white),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, -1), (-1, -1), 12),
    ]))
    elements.append(table)
    
    # Add footer
    elements.append(Spacer(1, 30))
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        alignment=TA_CENTER,
        fontSize=10,
        textColor=colors.HexColor('#7f8c8d')
    )
    elements.append(Paragraph("Thank you for choosing our services!", footer_style))
    elements.append(Paragraph("For any queries, please contact us at support@repaircenter.com", footer_style))
    
    # Build PDF
    doc.build(elements)

@app.route('/invoices/download/<int:invoice_id>')
@login_required
def download_invoice(invoice_id):
    pdf_file = f"invoices/invoice_{invoice_id}.pdf"
    return send_file(pdf_file, as_attachment=True)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # Check if passwords match
        if password != confirm_password:
            flash('Passwords do not match')
            return redirect(url_for('signup'))

        # Check if username already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('signup'))

        # Check if email already exists
        if User.query.filter_by(email=email).first():
            flash('Email already registered')
            return redirect(url_for('signup'))

        # Create new user
        new_user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            role='technician'  # Default role for new users
        )
        db.session.add(new_user)
        db.session.commit()

        flash('Account created successfully! Please login.')
        return redirect(url_for('login'))

    return render_template('signup.html')

if __name__ == '__main__':
    # Create necessary directories
    if not os.path.exists('invoices'):
        os.makedirs('invoices')
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    app.run(debug=True) 