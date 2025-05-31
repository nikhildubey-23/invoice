import tkinter as tk
from tkinter import ttk, messagebox
import csv
import os
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT

class RepairCenterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Laptop Repair Center Management System")
        self.root.geometry("1200x800")
        
        # Create data directory if it doesn't exist
        if not os.path.exists("data"):
            os.makedirs("data")
            
        # Initialize CSV files if they don't exist
        self.initialize_csv_files()
        
        # Create main notebook for tabs
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=5)
        
        # Create tabs
        self.create_customer_tab()
        self.create_device_tab()
        self.create_ticket_tab()
        self.create_service_tab()
        self.create_invoice_tab()
        self.create_summary_tab()
        
    def initialize_csv_files(self):
        """Initialize CSV files with headers if they don't exist"""
        files = {
            'data/customers.csv': ['customer_id', 'name', 'phone', 'email', 'address'],
            'data/devices.csv': ['device_id', 'customer_id', 'brand', 'model', 'serial_number', 'issue'],
            'data/tickets.csv': ['ticket_id', 'device_id', 'technician', 'status', 'created_date'],
            'data/services.csv': ['ticket_id', 'description', 'cost'],
            'data/invoices.csv': ['invoice_id', 'ticket_id', 'total_amount', 'paid_status', 'date', 'tax_rate', 'discount']
        }
        
        # Create data directory if it doesn't exist
        if not os.path.exists("data"):
            os.makedirs("data")
            
        # Create invoices directory if it doesn't exist
        if not os.path.exists("invoices"):
            os.makedirs("invoices")
        
        for file_path, headers in files.items():
            if not os.path.exists(file_path):
                try:
                    with open(file_path, 'w', newline='') as f:
                        writer = csv.writer(f)
                        writer.writerow(headers)
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to create {file_path}: {str(e)}")
    
    def create_customer_tab(self):
        """Create the customer management tab"""
        customer_frame = ttk.Frame(self.notebook)
        self.notebook.add(customer_frame, text='Customers')
        
        # Customer form
        form_frame = ttk.LabelFrame(customer_frame, text="Add/Edit Customer")
        form_frame.pack(fill='x', padx=5, pady=5)
        
        # Form fields
        ttk.Label(form_frame, text="Name:").grid(row=0, column=0, padx=5, pady=5)
        self.customer_name = ttk.Entry(form_frame)
        self.customer_name.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Phone:").grid(row=1, column=0, padx=5, pady=5)
        self.customer_phone = ttk.Entry(form_frame)
        self.customer_phone.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Email:").grid(row=2, column=0, padx=5, pady=5)
        self.customer_email = ttk.Entry(form_frame)
        self.customer_email.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Address:").grid(row=3, column=0, padx=5, pady=5)
        self.customer_address = ttk.Entry(form_frame)
        self.customer_address.grid(row=3, column=1, padx=5, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Add Customer", command=self.add_customer).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Clear Form", command=self.clear_customer_form).pack(side='left', padx=5)
        
        # Customer list
        list_frame = ttk.LabelFrame(customer_frame, text="Customer List")
        list_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Treeview for customer list
        columns = ('ID', 'Name', 'Phone', 'Email', 'Address')
        self.customer_tree = ttk.Treeview(list_frame, columns=columns, show='headings')
        
        for col in columns:
            self.customer_tree.heading(col, text=col)
            self.customer_tree.column(col, width=100)
        
        self.customer_tree.pack(fill='both', expand=True)
        
        # Add right-click menu for customer deletion
        self.customer_menu = tk.Menu(self.customer_tree, tearoff=0)
        self.customer_menu.add_command(label="Delete Customer", command=self.delete_customer)
        
        self.customer_tree.bind("<Button-3>", self.show_customer_menu)
        
        # Load initial customer data
        self.load_customers()

    def add_customer(self):
        """Add a new customer to the system"""
        # Get values from form
        name = self.customer_name.get().strip()
        phone = self.customer_phone.get().strip()
        email = self.customer_email.get().strip()
        address = self.customer_address.get().strip()
        
        # Validate required fields
        if not name:
            messagebox.showerror("Error", "Customer name is required!")
            return
        
        try:
            # Generate new customer ID
            customer_id = "1"
            if os.path.exists('data/customers.csv'):
                with open('data/customers.csv', 'r') as f:
                    reader = csv.DictReader(f)
                    customers = list(reader)
                    if customers:
                        customer_id = str(int(customers[-1]['customer_id']) + 1)
            
            # Add customer to CSV
            with open('data/customers.csv', 'a', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=['customer_id', 'name', 'phone', 'email', 'address'])
                writer.writerow({
                    'customer_id': customer_id,
                    'name': name,
                    'phone': phone,
                    'email': email,
                    'address': address
                })
            
            # Clear form and refresh list
            self.clear_customer_form()
            self.load_customers()
            self.load_customer_combo()  # Refresh customer combo in device tab
            
            messagebox.showinfo("Success", f"Customer '{name}' has been added.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add customer: {str(e)}")

    def clear_customer_form(self):
        """Clear the customer form fields"""
        self.customer_name.delete(0, tk.END)
        self.customer_phone.delete(0, tk.END)
        self.customer_email.delete(0, tk.END)
        self.customer_address.delete(0, tk.END)

    def load_customers(self):
        """Load customers from CSV into the treeview"""
        # Clear existing items
        for item in self.customer_tree.get_children():
            self.customer_tree.delete(item)
        
        # Load from CSV
        try:
            with open('data/customers.csv', 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    self.customer_tree.insert('', 'end', values=(
                        row['customer_id'],
                        row['name'],
                        row['phone'],
                        row['email'],
                        row['address']
                    ))
        except FileNotFoundError:
            pass
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load customers: {str(e)}")

    def load_customer_combo(self):
        """Load customers into the combo box for device creation"""
        try:
            customers = []
            with open('data/customers.csv', 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    customers.append(f"{row['name']} (ID: {row['customer_id']})")
            self.customer_combo['values'] = customers
        except FileNotFoundError:
            self.customer_combo['values'] = []
        except Exception as e:
            print(f"Error loading customer combo: {str(e)}")
            self.customer_combo['values'] = []

    def show_customer_menu(self, event):
        """Show the right-click menu for customer deletion"""
        item = self.customer_tree.identify_row(event.y)
        if item:
            self.customer_tree.selection_set(item)
            self.customer_menu.post(event.x_root, event.y_root)

    def delete_customer(self):
        """Delete the selected customer"""
        selected_item = self.customer_tree.selection()
        if not selected_item:
            return
        
        customer_id = self.customer_tree.item(selected_item[0])['values'][0]
        customer_name = self.customer_tree.item(selected_item[0])['values'][1]
        
        # Confirm deletion
        if not messagebox.askyesno("Confirm Deletion", 
            f"Are you sure you want to delete customer '{customer_name}'?\n\n"
            "This will also delete all associated devices, tickets, services, and invoices!"):
            return
        
        try:
            # Delete customer
            customers = []
            with open('data/customers.csv', 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row['customer_id'] != customer_id:
                        customers.append(row)
            
            with open('data/customers.csv', 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=['customer_id', 'name', 'phone', 'email', 'address'])
                writer.writeheader()
                writer.writerows(customers)
            
            # Delete associated devices
            devices = []
            device_ids = []
            try:
                with open('data/devices.csv', 'r') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        if row['customer_id'] != customer_id:
                            devices.append(row)
                        else:
                            device_ids.append(row['device_id'])
                
                with open('data/devices.csv', 'w', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=['device_id', 'customer_id', 'brand', 'model', 'serial_number', 'issue'])
                    writer.writeheader()
                    writer.writerows(devices)
            except FileNotFoundError:
                pass
            
            # Delete associated tickets
            tickets = []
            ticket_ids = []
            try:
                with open('data/tickets.csv', 'r') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        if row['device_id'] not in device_ids:
                            tickets.append(row)
                        else:
                            ticket_ids.append(row['ticket_id'])
                
                with open('data/tickets.csv', 'w', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=['ticket_id', 'device_id', 'technician', 'status', 'created_date'])
                    writer.writeheader()
                    writer.writerows(tickets)
            except FileNotFoundError:
                pass
            
            # Delete associated services
            services = []
            try:
                with open('data/services.csv', 'r') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        if row['ticket_id'] not in ticket_ids:
                            services.append(row)
                
                with open('data/services.csv', 'w', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=['ticket_id', 'description', 'cost'])
                    writer.writeheader()
                    writer.writerows(services)
            except FileNotFoundError:
                pass
            
            # Delete associated invoices
            invoices = []
            try:
                with open('data/invoices.csv', 'r') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        if row['ticket_id'] not in ticket_ids:
                            invoices.append(row)
                
                with open('data/invoices.csv', 'w', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=['invoice_id', 'ticket_id', 'total_amount', 'paid_status', 'date', 'tax_rate', 'discount'])
                    writer.writeheader()
                    writer.writerows(invoices)
            except FileNotFoundError:
                pass
            
            # Refresh all lists
            self.load_customers()
            self.load_devices()
            self.load_tickets()
            self.load_services()
            self.load_invoices()
            self.load_customer_combo()
            
            messagebox.showinfo("Success", f"Customer '{customer_name}' and all associated records have been deleted.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete customer: {str(e)}")
    
    def create_device_tab(self):
        """Create the device management tab"""
        device_frame = ttk.Frame(self.notebook)
        self.notebook.add(device_frame, text='Devices')
        
        # Device form
        form_frame = ttk.LabelFrame(device_frame, text="Add New Device")
        form_frame.pack(fill='x', padx=5, pady=5)
        
        # Customer selection
        ttk.Label(form_frame, text="Customer:").grid(row=0, column=0, padx=5, pady=5)
        self.customer_var = tk.StringVar()
        self.customer_combo = ttk.Combobox(form_frame, textvariable=self.customer_var, width=40)
        self.customer_combo.grid(row=0, column=1, padx=5, pady=5)
        
        # Add refresh button for customer list
        ttk.Button(form_frame, text="Refresh Customers", command=self.load_customer_combo).grid(row=0, column=2, padx=5, pady=5)
        
        # Device details
        ttk.Label(form_frame, text="Brand:").grid(row=1, column=0, padx=5, pady=5)
        self.device_brand = ttk.Entry(form_frame)
        self.device_brand.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Model:").grid(row=2, column=0, padx=5, pady=5)
        self.device_model = ttk.Entry(form_frame)
        self.device_model.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Serial Number:").grid(row=3, column=0, padx=5, pady=5)
        self.device_serial = ttk.Entry(form_frame)
        self.device_serial.grid(row=3, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Issue:").grid(row=4, column=0, padx=5, pady=5)
        self.device_issue = tk.Text(form_frame, height=3, width=30)
        self.device_issue.grid(row=4, column=1, padx=5, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Add Device", command=self.add_device).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Clear Form", command=self.clear_device_form).pack(side='left', padx=5)
        
        # Device list
        list_frame = ttk.LabelFrame(device_frame, text="Device List")
        list_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Treeview for device list
        columns = ('ID', 'Customer', 'Brand', 'Model', 'Serial Number', 'Issue')
        self.device_tree = ttk.Treeview(list_frame, columns=columns, show='headings')
        
        for col in columns:
            self.device_tree.heading(col, text=col)
            self.device_tree.column(col, width=100)
        
        self.device_tree.pack(fill='both', expand=True)
        
        # Add right-click menu for device deletion
        self.device_menu = tk.Menu(self.device_tree, tearoff=0)
        self.device_menu.add_command(label="Delete Device", command=self.delete_device)
        
        self.device_tree.bind("<Button-3>", self.show_device_menu)
        
        # Load initial device data
        self.load_devices()
        self.load_customer_combo()

    def add_device(self):
        """Add a new device to the system"""
        # Get values from form
        customer = self.customer_var.get().strip()
        brand = self.device_brand.get().strip()
        model = self.device_model.get().strip()
        serial = self.device_serial.get().strip()
        issue = self.device_issue.get("1.0", tk.END).strip()
        
        # Validate required fields
        if not customer or not brand or not model:
            messagebox.showerror("Error", "Customer, brand, and model are required!")
            return
        
        try:
            # Extract customer ID from the combo box selection
            customer_id = customer.split("(ID: ")[-1].rstrip(")")
            
            # Generate new device ID
            device_id = "1"
            if os.path.exists('data/devices.csv'):
                with open('data/devices.csv', 'r') as f:
                    reader = csv.DictReader(f)
                    devices = list(reader)
                    if devices:
                        device_id = str(int(devices[-1]['device_id']) + 1)
            
            # Add device to CSV
            with open('data/devices.csv', 'a', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=['device_id', 'customer_id', 'brand', 'model', 'serial_number', 'issue'])
                writer.writerow({
                    'device_id': device_id,
                    'customer_id': customer_id,
                    'brand': brand,
                    'model': model,
                    'serial_number': serial,
                    'issue': issue
                })
            
            # Clear form and refresh list
            self.clear_device_form()
            self.load_devices()
            self.load_device_combo()  # Refresh device combo in ticket tab
            
            messagebox.showinfo("Success", f"Device '{brand} {model}' has been added.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add device: {str(e)}")

    def clear_device_form(self):
        """Clear the device form fields"""
        self.customer_var.set('')
        self.device_brand.delete(0, tk.END)
        self.device_model.delete(0, tk.END)
        self.device_serial.delete(0, tk.END)
        self.device_issue.delete("1.0", tk.END)

    def load_devices(self):
        """Load devices from CSV into the treeview"""
        # Clear existing items
        for item in self.device_tree.get_children():
            self.device_tree.delete(item)
        
        # Load from CSV
        try:
            with open('data/devices.csv', 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Get customer name
                    customer_name = "Unknown"
                    try:
                        with open('data/customers.csv', 'r') as c:
                            customer_reader = csv.DictReader(c)
                            for customer in customer_reader:
                                if customer['customer_id'] == row['customer_id']:
                                    customer_name = customer['name']
                                    break
                    except Exception as e:
                        print(f"Error getting customer name: {str(e)}")
                    
                    self.device_tree.insert('', 'end', values=(
                        row['device_id'],
                        customer_name,
                        row['brand'],
                        row['model'],
                        row['serial_number'],
                        row['issue']
                    ))
        except FileNotFoundError:
            pass
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load devices: {str(e)}")

    def load_device_combo(self):
        """Load devices into the combo box for ticket creation"""
        try:
            devices = []
            with open('data/devices.csv', 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Get customer name
                    customer_name = "Unknown"
                    try:
                        with open('data/customers.csv', 'r') as c:
                            customer_reader = csv.DictReader(c)
                            for customer in customer_reader:
                                if customer['customer_id'] == row['customer_id']:
                                    customer_name = customer['name']
                                    break
                    except Exception as e:
                        print(f"Error getting customer name: {str(e)}")
                    
                    devices.append(f"{row['brand']} {row['model']} - {customer_name} (ID: {row['device_id']})")
            self.device_combo['values'] = devices
        except FileNotFoundError:
            self.device_combo['values'] = []
        except Exception as e:
            print(f"Error loading device combo: {str(e)}")
            self.device_combo['values'] = []

    def show_device_menu(self, event):
        """Show the right-click menu for device deletion"""
        item = self.device_tree.identify_row(event.y)
        if item:
            self.device_tree.selection_set(item)
            self.device_menu.post(event.x_root, event.y_root)

    def delete_device(self):
        """Delete the selected device"""
        selected_item = self.device_tree.selection()
        if not selected_item:
            return
        
        device_id = self.device_tree.item(selected_item[0])['values'][0]
        device_info = f"{self.device_tree.item(selected_item[0])['values'][2]} {self.device_tree.item(selected_item[0])['values'][3]}"
        
        # Confirm deletion
        if not messagebox.askyesno("Confirm Deletion", 
            f"Are you sure you want to delete device '{device_info}'?\n\n"
            "This will also delete all associated tickets, services, and invoices!"):
            return
        
        try:
            # Delete device
            devices = []
            with open('data/devices.csv', 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row['device_id'] != device_id:
                        devices.append(row)
            
            with open('data/devices.csv', 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=['device_id', 'customer_id', 'brand', 'model', 'serial_number', 'issue'])
                writer.writeheader()
                writer.writerows(devices)
            
            # Delete associated tickets
            tickets = []
            ticket_ids = []
            with open('data/tickets.csv', 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row['device_id'] != device_id:
                        tickets.append(row)
                    else:
                        ticket_ids.append(row['ticket_id'])
            
            with open('data/tickets.csv', 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=['ticket_id', 'device_id', 'technician', 'status', 'created_date'])
                writer.writeheader()
                writer.writerows(tickets)
            
            # Delete associated services
            services = []
            with open('data/services.csv', 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row['ticket_id'] not in ticket_ids:
                        services.append(row)
            
            with open('data/services.csv', 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=['ticket_id', 'description', 'cost'])
                writer.writeheader()
                writer.writerows(services)
            
            # Delete associated invoices
            invoices = []
            with open('data/invoices.csv', 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row['ticket_id'] not in ticket_ids:
                        invoices.append(row)
            
            with open('data/invoices.csv', 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=['invoice_id', 'ticket_id', 'total_amount', 'paid_status', 'date', 'tax_rate', 'discount'])
                writer.writeheader()
                writer.writerows(invoices)
            
            # Refresh all lists
            self.load_devices()
            self.load_tickets()
            self.load_services()
            self.load_invoices()
            
            messagebox.showinfo("Success", f"Device '{device_info}' and all associated records have been deleted.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete device: {str(e)}")
    
    def create_ticket_tab(self):
        """Create the repair ticket management tab"""
        ticket_frame = ttk.Frame(self.notebook)
        self.notebook.add(ticket_frame, text='Tickets')
        
        # Ticket form
        form_frame = ttk.LabelFrame(ticket_frame, text="Create New Ticket")
        form_frame.pack(fill='x', padx=5, pady=5)
        
        # Device selection
        ttk.Label(form_frame, text="Device:").grid(row=0, column=0, padx=5, pady=5)
        self.device_var = tk.StringVar()
        self.device_combo = ttk.Combobox(form_frame, textvariable=self.device_var, width=40)
        self.device_combo.grid(row=0, column=1, padx=5, pady=5)
        self.load_device_combo()
        
        # Add refresh button for device list
        ttk.Button(form_frame, text="Refresh Devices", command=self.load_device_combo).grid(row=0, column=2, padx=5, pady=5)
        
        # Technician
        ttk.Label(form_frame, text="Technician:").grid(row=1, column=0, padx=5, pady=5)
        self.technician_var = tk.StringVar()
        self.technician_combo = ttk.Combobox(form_frame, textvariable=self.technician_var)
        self.technician_combo['values'] = ['John Doe', 'Jane Smith', 'Mike Johnson']
        self.technician_combo.grid(row=1, column=1, padx=5, pady=5)
        
        # Status
        ttk.Label(form_frame, text="Status:").grid(row=2, column=0, padx=5, pady=5)
        self.status_var = tk.StringVar(value="Received")
        status_combo = ttk.Combobox(form_frame, textvariable=self.status_var)
        status_combo['values'] = ['Received', 'In Progress', 'Completed']
        status_combo.grid(row=2, column=1, padx=5, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Create Ticket", command=self.add_ticket).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Clear Form", command=self.clear_ticket_form).pack(side='left', padx=5)
        
        # Ticket list
        list_frame = ttk.LabelFrame(ticket_frame, text="Ticket List")
        list_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Treeview for ticket list
        columns = ('ID', 'Device', 'Customer', 'Technician', 'Status', 'Created Date')
        self.ticket_tree = ttk.Treeview(list_frame, columns=columns, show='headings')
        
        for col in columns:
            self.ticket_tree.heading(col, text=col)
            self.ticket_tree.column(col, width=100)
        
        self.ticket_tree.pack(fill='both', expand=True)
        
        # Add right-click menu for ticket deletion
        self.ticket_menu = tk.Menu(self.ticket_tree, tearoff=0)
        self.ticket_menu.add_command(label="Delete Ticket", command=self.delete_ticket)
        
        self.ticket_tree.bind("<Button-3>", self.show_ticket_menu)
        
        # Load initial ticket data
        self.load_tickets()

    def add_ticket(self):
        """Add a new repair ticket to the system"""
        # Get values from form
        device = self.device_var.get().strip()
        technician = self.technician_var.get().strip()
        status = self.status_var.get().strip()
        
        # Validate required fields
        if not device or not technician:
            messagebox.showerror("Error", "Device and technician are required!")
            return
        
        try:
            # Extract device ID from the combo box selection
            device_id = device.split("(ID: ")[-1].rstrip(")")
            
            # Generate new ticket ID
            ticket_id = "1"
            if os.path.exists('data/tickets.csv'):
                with open('data/tickets.csv', 'r') as f:
                    reader = csv.DictReader(f)
                    tickets = list(reader)
                    if tickets:
                        ticket_id = str(int(tickets[-1]['ticket_id']) + 1)
            
            # Get current date
            created_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Add ticket to CSV
            with open('data/tickets.csv', 'a', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=['ticket_id', 'device_id', 'technician', 'status', 'created_date'])
                writer.writerow({
                    'ticket_id': ticket_id,
                    'device_id': device_id,
                    'technician': technician,
                    'status': status,
                    'created_date': created_date
                })
            
            # Clear form and refresh list
            self.clear_ticket_form()
            self.load_tickets()
            self.load_ticket_combo()  # Refresh ticket combo in service tab
            self.load_invoice_ticket_combo()  # Refresh ticket combo in invoice tab
            
            messagebox.showinfo("Success", f"Ticket #{ticket_id} has been created.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create ticket: {str(e)}")

    def clear_ticket_form(self):
        """Clear the ticket form fields"""
        self.device_var.set('')
        self.technician_var.set('')
        self.status_var.set("Received")

    def load_tickets(self):
        """Load tickets from CSV into the treeview"""
        # Clear existing items
        for item in self.ticket_tree.get_children():
            self.ticket_tree.delete(item)
        
        # Load from CSV
        try:
            with open('data/tickets.csv', 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Get device and customer info
                    device_info = self.get_device_info(row['device_id'])
                    customer_name = self.get_customer_name(device_info['customer_id'])
                    
                    self.ticket_tree.insert('', 'end', values=(
                        row['ticket_id'],
                        f"{device_info['brand']} {device_info['model']}",
                        customer_name,
                        row['technician'],
                        row['status'],
                        row['created_date']
                    ))
        except FileNotFoundError:
            pass
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load tickets: {str(e)}")

    def load_ticket_combo(self):
        """Load tickets into the combo box for service creation"""
        try:
            tickets = []
            with open('data/tickets.csv', 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Get device and customer info
                    device_info = self.get_device_info(row['device_id'])
                    customer_name = self.get_customer_name(device_info['customer_id'])
                    
                    tickets.append(f"Ticket #{row['ticket_id']} - {device_info['brand']} {device_info['model']} ({customer_name})")
            self.service_ticket_combo['values'] = tickets
        except FileNotFoundError:
            self.service_ticket_combo['values'] = []
        except Exception as e:
            print(f"Error loading ticket combo: {str(e)}")
            self.service_ticket_combo['values'] = []

    def load_invoice_ticket_combo(self):
        """Load completed tickets into the combo box for invoice creation"""
        try:
            tickets = []
            debug_info = []
            
            # Check if tickets.csv exists
            if not os.path.exists('data/tickets.csv'):
                debug_info.append("tickets.csv not found")
                messagebox.showerror("Error", "tickets.csv file not found. Please create some tickets first.")
                self.invoice_ticket_combo['values'] = []
                return
            
            # Check if services.csv exists
            if not os.path.exists('data/services.csv'):
                debug_info.append("services.csv not found")
                messagebox.showerror("Error", "services.csv file not found. Please add some services first.")
                self.invoice_ticket_combo['values'] = []
                return
                
            # Read tickets
            with open('data/tickets.csv', 'r') as f:
                reader = csv.DictReader(f)
                tickets_data = list(reader)
                debug_info.append(f"Total tickets found: {len(tickets_data)}")
                
                if len(tickets_data) == 0:
                    debug_info.append("No tickets found in the system")
                    messagebox.showwarning("No Tickets", "No tickets found in the system. Please create some tickets first.")
                    self.invoice_ticket_combo['values'] = []
                    return
                
                # Debug ticket statuses
                status_counts = {}
                for ticket in tickets_data:
                    status = ticket['status']
                    status_counts[status] = status_counts.get(status, 0) + 1
                debug_info.append("\nTicket Status Counts:")
                for status, count in status_counts.items():
                    debug_info.append(f"- {status}: {count}")
                
                # Check if any completed tickets exist
                if 'Completed' not in status_counts:
                    debug_info.append("\nNo completed tickets found")
                    messagebox.showwarning("No Completed Tickets", "No completed tickets found. Please complete some tickets first.")
                    self.invoice_ticket_combo['values'] = []
                    return
                
                for row in tickets_data:
                    debug_info.append(f"\nChecking Ticket #{row['ticket_id']}:")
                    debug_info.append(f"- Status: {row['status']}")
                    
                    if row['status'] == 'Completed':
                        # Get device and customer info
                        device_info = self.get_device_info(row['device_id'])
                        customer_name = self.get_customer_name(device_info['customer_id'])
                        debug_info.append(f"- Device: {device_info['brand']} {device_info['model']}")
                        debug_info.append(f"- Customer: {customer_name}")
                        
                        # Check if ticket already has an invoice
                        has_invoice = False
                        try:
                            if os.path.exists('data/invoices.csv'):
                                with open('data/invoices.csv', 'r') as i:
                                    invoice_reader = csv.DictReader(i)
                                    for invoice in invoice_reader:
                                        if invoice['ticket_id'] == row['ticket_id']:
                                            has_invoice = True
                                            debug_info.append(f"- Already has an invoice")
                                            break
                        except FileNotFoundError:
                            debug_info.append("- No invoices.csv file found")
                        
                        if not has_invoice:
                            # Check if ticket has services
                            has_services = False
                            service_count = 0
                            try:
                                with open('data/services.csv', 'r') as s:
                                    service_reader = csv.DictReader(s)
                                    for service in service_reader:
                                        if service['ticket_id'] == row['ticket_id']:
                                            has_services = True
                                            service_count += 1
                                    debug_info.append(f"- Services found: {service_count}")
                            except FileNotFoundError:
                                debug_info.append("- Error reading services.csv")
                            
                            if has_services:
                                ticket_text = f"Ticket #{row['ticket_id']} - {device_info['brand']} {device_info['model']} ({customer_name})"
                                tickets.append(ticket_text)
                                debug_info.append(f"- Added to available tickets list: {ticket_text}")
                            else:
                                debug_info.append("- Not added: No services found")
                    else:
                        debug_info.append("- Not added: Status is not 'Completed'")
            
            # Update the combo box
            self.invoice_ticket_combo['values'] = tickets
            
            # If no tickets are available, show debug info
            if not tickets:
                debug_message = "No tickets available for invoice generation.\n\nDebug Information:\n" + "\n".join(debug_info)
                messagebox.showwarning("No Tickets Available", debug_message)
            else:
                debug_info.append(f"\nTotal tickets available for invoice generation: {len(tickets)}")
                print("\n".join(debug_info))  # Print debug info to console for reference
                
        except FileNotFoundError:
            self.invoice_ticket_combo['values'] = []
            messagebox.showerror("Error", "Required files not found. Please ensure all data files exist.")
        except Exception as e:
            print(f"Error loading invoice ticket combo: {str(e)}")
            self.invoice_ticket_combo['values'] = []
            messagebox.showerror("Error", f"Failed to load tickets: {str(e)}")

    def get_device_info(self, device_id):
        """Get device information from the device ID"""
        try:
            if not os.path.exists('data/devices.csv'):
                print(f"devices.csv not found for device_id: {device_id}")
                return {'brand': 'Unknown', 'model': 'Unknown', 'customer_id': 'Unknown'}
                
            with open('data/devices.csv', 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row['device_id'] == device_id:
                        return row
            print(f"No device found for device_id: {device_id}")
            return {'brand': 'Unknown', 'model': 'Unknown', 'customer_id': 'Unknown'}
        except Exception as e:
            print(f"Error getting device info: {str(e)}")
            return {'brand': 'Error', 'model': 'Error', 'customer_id': 'Error'}

    def get_customer_name(self, customer_id):
        """Get customer name from the customer ID"""
        try:
            if not os.path.exists('data/customers.csv'):
                print(f"customers.csv not found for customer_id: {customer_id}")
                return "Unknown"
                
            with open('data/customers.csv', 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row['customer_id'] == customer_id:
                        return row['name']
            print(f"No customer found for customer_id: {customer_id}")
            return "Unknown"
        except Exception as e:
            print(f"Error getting customer name: {str(e)}")
            return "Error"

    def show_ticket_menu(self, event):
        """Show the right-click menu for ticket deletion"""
        item = self.ticket_tree.identify_row(event.y)
        if item:
            self.ticket_tree.selection_set(item)
            self.ticket_menu.post(event.x_root, event.y_root)

    def delete_ticket(self):
        """Delete the selected ticket"""
        selected_item = self.ticket_tree.selection()
        if not selected_item:
            return
        
        ticket_id = self.ticket_tree.item(selected_item[0])['values'][0]
        ticket_info = f"Ticket #{ticket_id}"
        
        # Confirm deletion
        if not messagebox.askyesno("Confirm Deletion", 
            f"Are you sure you want to delete {ticket_info}?\n\n"
            "This will also delete all associated services and invoices!"):
            return
        
        try:
            # Delete ticket
            tickets = []
            with open('data/tickets.csv', 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row['ticket_id'] != ticket_id:
                        tickets.append(row)
            
            with open('data/tickets.csv', 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=['ticket_id', 'device_id', 'technician', 'status', 'created_date'])
                writer.writeheader()
                writer.writerows(tickets)
            
            # Delete associated services
            services = []
            with open('data/services.csv', 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row['ticket_id'] not in ticket_ids:
                        services.append(row)
            
            with open('data/services.csv', 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=['ticket_id', 'description', 'cost'])
                writer.writeheader()
                writer.writerows(services)
            
            # Delete associated invoices
            invoices = []
            with open('data/invoices.csv', 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row['ticket_id'] not in ticket_ids:
                        invoices.append(row)
            
            with open('data/invoices.csv', 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=['invoice_id', 'ticket_id', 'total_amount', 'paid_status', 'date', 'tax_rate', 'discount'])
                writer.writeheader()
                writer.writerows(invoices)
            
            # Refresh all lists
            self.load_tickets()
            self.load_services()
            self.load_invoices()
            
            messagebox.showinfo("Success", f"{ticket_info} and all associated records have been deleted.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete ticket: {str(e)}")
    
    def create_service_tab(self):
        """Create the parts and services tab"""
        service_frame = ttk.Frame(self.notebook)
        self.notebook.add(service_frame, text='Services')
        
        # Service form
        form_frame = ttk.LabelFrame(service_frame, text="Add Service/Part")
        form_frame.pack(fill='x', padx=5, pady=5)
        
        # Ticket selection
        ttk.Label(form_frame, text="Ticket:").grid(row=0, column=0, padx=5, pady=5)
        self.service_ticket_var = tk.StringVar()
        self.service_ticket_combo = ttk.Combobox(form_frame, textvariable=self.service_ticket_var, width=50, state="readonly")
        self.service_ticket_combo.grid(row=0, column=1, padx=5, pady=5)
        
        # Add refresh button for ticket list
        refresh_btn = ttk.Button(form_frame, text="Refresh Tickets", command=self.load_service_ticket_combo)
        refresh_btn.grid(row=0, column=2, padx=5, pady=5)
        
        # Description
        ttk.Label(form_frame, text="Description:").grid(row=1, column=0, padx=5, pady=5)
        self.service_desc = tk.Text(form_frame, height=3, width=30)
        self.service_desc.grid(row=1, column=1, padx=5, pady=5)
        
        # Cost
        ttk.Label(form_frame, text="Cost (₹):").grid(row=2, column=0, padx=5, pady=5)
        self.service_cost = ttk.Entry(form_frame)
        self.service_cost.grid(row=2, column=1, padx=5, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Add Service", command=self.add_service).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Clear Form", command=self.clear_service_form).pack(side='left', padx=5)
        
        # Service list
        list_frame = ttk.LabelFrame(service_frame, text="Service List")
        list_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Treeview for service list
        columns = ('Ticket', 'Device', 'Customer', 'Description', 'Cost')
        self.service_tree = ttk.Treeview(list_frame, columns=columns, show='headings')
        
        for col in columns:
            self.service_tree.heading(col, text=col)
            self.service_tree.column(col, width=100)
        
        self.service_tree.pack(fill='both', expand=True)
        
        # Add right-click menu for service deletion
        self.service_menu = tk.Menu(self.service_tree, tearoff=0)
        self.service_menu.add_command(label="Delete Service", command=self.delete_service)
        
        self.service_tree.bind("<Button-3>", self.show_service_menu)
        
        # Load initial service data
        self.load_services()
        self.load_service_ticket_combo()
    
    def show_service_menu(self, event):
        """Show the right-click menu for service deletion"""
        item = self.service_tree.identify_row(event.y)
        if item:
            self.service_tree.selection_set(item)
            self.service_menu.post(event.x_root, event.y_root)

    def delete_service(self):
        """Delete the selected service"""
        selected_item = self.service_tree.selection()
        if not selected_item:
            return
        
        service_info = self.service_tree.item(selected_item[0])['values']
        ticket_id = service_info[0].split("Ticket #")[1]
        description = service_info[3]
        
        # Confirm deletion
        if not messagebox.askyesno("Confirm Deletion", 
            f"Are you sure you want to delete this service?\n\n"
            f"Ticket: #{ticket_id}\n"
            f"Description: {description}"):
            return
        
        try:
            # Delete service
            services = []
            with open('data/services.csv', 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if not (row['ticket_id'] == ticket_id and row['description'] == description):
                        services.append(row)
            
            with open('data/services.csv', 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=['ticket_id', 'description', 'cost'])
                writer.writeheader()
                writer.writerows(services)
            
            # Refresh service list
            self.load_services()
            messagebox.showinfo("Success", "Service has been deleted.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete service: {str(e)}")
    
    def create_invoice_tab(self):
        """Create the invoice generation tab"""
        invoice_frame = ttk.Frame(self.notebook)
        self.notebook.add(invoice_frame, text='Invoices')
        
        # Create a frame for the two sections
        sections_frame = ttk.Frame(invoice_frame)
        sections_frame.pack(fill='x', padx=5, pady=5)
        
        # Left section - Generate Invoice
        left_frame = ttk.LabelFrame(sections_frame, text="Generate Invoice")
        left_frame.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        
        # Ticket selection
        ttk.Label(left_frame, text="Ticket:").grid(row=0, column=0, padx=5, pady=5)
        self.invoice_ticket_var = tk.StringVar()
        self.invoice_ticket_combo = ttk.Combobox(left_frame, textvariable=self.invoice_ticket_var, width=50, state="readonly")
        self.invoice_ticket_combo.grid(row=0, column=1, padx=5, pady=5)
        
        # Add refresh button for ticket list
        refresh_btn = ttk.Button(left_frame, text="Refresh Tickets", command=self.load_invoice_ticket_combo)
        refresh_btn.grid(row=0, column=2, padx=5, pady=5)
        
        # Add debug button
        debug_btn = ttk.Button(left_frame, text="Debug Info", command=self.show_debug_info)
        debug_btn.grid(row=0, column=3, padx=5, pady=5)
        
        # Tax rate
        ttk.Label(left_frame, text="Tax Rate (%):").grid(row=1, column=0, padx=5, pady=5)
        self.tax_rate = ttk.Entry(left_frame)
        self.tax_rate.insert(0, "0")
        self.tax_rate.grid(row=1, column=1, padx=5, pady=5)
        
        # Discount
        ttk.Label(left_frame, text="Discount (₹):").grid(row=2, column=0, padx=5, pady=5)
        self.discount = ttk.Entry(left_frame)
        self.discount.insert(0, "0")
        self.discount.grid(row=2, column=1, padx=5, pady=5)
        
        # Payment Status
        ttk.Label(left_frame, text="Payment Status:").grid(row=3, column=0, padx=5, pady=5)
        self.payment_status_var = tk.StringVar(value="Unpaid")
        self.payment_status_combo = ttk.Combobox(left_frame, textvariable=self.payment_status_var, state="readonly")
        self.payment_status_combo['values'] = ['Paid', 'Unpaid']
        self.payment_status_combo.grid(row=3, column=1, padx=5, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(left_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Generate Invoice", command=self.generate_invoice).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Clear Form", command=self.clear_invoice_form).pack(side='left', padx=5)
        
        # Right section - Manual Amount Entry
        right_frame = ttk.LabelFrame(sections_frame, text="Manual Amount Entry")
        right_frame.pack(side='right', fill='both', expand=True, padx=5, pady=5)
        
        # Amount
        ttk.Label(right_frame, text="Amount (₹):").grid(row=0, column=0, padx=5, pady=5)
        self.manual_amount = ttk.Entry(right_frame)
        self.manual_amount.insert(0, "0")
        self.manual_amount.grid(row=0, column=1, padx=5, pady=5)
        
        # Manual Tax Rate
        ttk.Label(right_frame, text="Tax Rate (%):").grid(row=1, column=0, padx=5, pady=5)
        self.manual_tax_rate = ttk.Entry(right_frame)
        self.manual_tax_rate.insert(0, "0")
        self.manual_tax_rate.grid(row=1, column=1, padx=5, pady=5)
        
        # Manual Discount
        ttk.Label(right_frame, text="Discount (₹):").grid(row=2, column=0, padx=5, pady=5)
        self.manual_discount = ttk.Entry(right_frame)
        self.manual_discount.insert(0, "0")
        self.manual_discount.grid(row=2, column=1, padx=5, pady=5)
        
        # Total Amount (Read-only)
        ttk.Label(right_frame, text="Total Amount (₹):").grid(row=3, column=0, padx=5, pady=5)
        self.total_amount_var = tk.StringVar(value="₹0.00")
        self.total_amount_label = ttk.Label(right_frame, textvariable=self.total_amount_var, font=('Helvetica', 10, 'bold'))
        self.total_amount_label.grid(row=3, column=1, padx=5, pady=5)
        
        # Calculate button
        ttk.Button(right_frame, text="Calculate Total", command=self.calculate_manual_total).grid(row=4, column=0, columnspan=2, pady=10)
        
        # Invoice list
        list_frame = ttk.LabelFrame(invoice_frame, text="Invoice List")
        list_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Treeview for invoice list
        columns = ('ID', 'Ticket', 'Customer', 'Total Amount', 'Status', 'Date')
        self.invoice_tree = ttk.Treeview(list_frame, columns=columns, show='headings')
        
        # Configure column widths
        self.invoice_tree.column('ID', width=50)
        self.invoice_tree.column('Ticket', width=100)
        self.invoice_tree.column('Customer', width=150)
        self.invoice_tree.column('Total Amount', width=100)
        self.invoice_tree.column('Status', width=100)
        self.invoice_tree.column('Date', width=150)
        
        for col in columns:
            self.invoice_tree.heading(col, text=col)
        
        self.invoice_tree.pack(fill='both', expand=True)
        
        # Add right-click menu for invoice status updates
        self.invoice_menu = tk.Menu(self.invoice_tree, tearoff=0)
        self.invoice_menu.add_command(label="Mark as Paid", command=lambda: self.update_invoice_status("Paid"))
        self.invoice_menu.add_command(label="Mark as Unpaid", command=lambda: self.update_invoice_status("Unpaid"))
        self.invoice_menu.add_command(label="Delete Invoice", command=self.delete_invoice)
        
        self.invoice_tree.bind("<Button-3>", self.show_invoice_menu)
        
        # Load initial data
        self.load_invoices()
        self.load_invoice_ticket_combo()

    def calculate_manual_total(self):
        """Calculate total amount from manual entry"""
        try:
            # Get values from entries
            amount = float(self.manual_amount.get().strip() or 0)
            tax_rate = float(self.manual_tax_rate.get().strip() or 0)
            discount = float(self.manual_discount.get().strip() or 0)
            
            # Calculate tax amount
            tax_amount = amount * (tax_rate / 100)
            
            # Calculate total
            total = amount + tax_amount - discount
            
            # Ensure total is not negative
            total = max(0, total)
            
            # Update total amount label
            self.total_amount_var.set(f"₹{total:.2f}")
            
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for amount, tax rate, and discount!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to calculate total: {str(e)}")

    def clear_invoice_form(self):
        """Clear the invoice form fields"""
        self.invoice_ticket_var.set('')
        self.tax_rate.delete(0, tk.END)
        self.tax_rate.insert(0, "0")
        self.discount.delete(0, tk.END)
        self.discount.insert(0, "0")
        self.payment_status_var.set("Unpaid")
        
        # Clear manual amount section
        self.manual_amount.delete(0, tk.END)
        self.manual_amount.insert(0, "0")
        self.manual_tax_rate.delete(0, tk.END)
        self.manual_tax_rate.insert(0, "0")
        self.manual_discount.delete(0, tk.END)
        self.manual_discount.insert(0, "0")
        self.total_amount_var.set("₹0.00")
        
        # Reload ticket combo to ensure it's up to date
        self.load_invoice_ticket_combo()

    def get_ticket_info(self, ticket_id):
        """Get ticket information including customer details"""
        try:
            # Get ticket info
            with open('data/tickets.csv', 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row['ticket_id'] == ticket_id:
                        device_id = row['device_id']
                        # Get device info
                        with open('data/devices.csv', 'r') as d:
                            device_reader = csv.DictReader(d)
                            for device in device_reader:
                                if device['device_id'] == device_id:
                                    customer_id = device['customer_id']
                                    # Get customer info
                                    with open('data/customers.csv', 'r') as c:
                                        customer_reader = csv.DictReader(c)
                                        for customer in customer_reader:
                                            if customer['customer_id'] == customer_id:
                                                return {
                                                    'customer': customer['name'],
                                                    'device': f"{device['brand']} {device['model']}",
                                                    'status': row['status']
                                                }
            return {'customer': 'Unknown', 'device': 'Unknown', 'status': 'Unknown'}
        except Exception as e:
            print(f"Error getting ticket info: {str(e)}")
            return {'customer': 'Error', 'device': 'Error', 'status': 'Error'}

    def load_invoices(self):
        """Load invoices from CSV into the treeview"""
        # Clear existing items
        for item in self.invoice_tree.get_children():
            self.invoice_tree.delete(item)
        
        # Load from CSV
        try:
            with open('data/invoices.csv', 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        # Get ticket and customer info
                        ticket_info = self.get_ticket_info(row['ticket_id'])
                        
                        # Calculate total amount from services
                        total_amount = 0
                        try:
                            with open('data/services.csv', 'r') as services_file:
                                services_reader = csv.DictReader(services_file)
                                for service in services_reader:
                                    if service['ticket_id'] == row['ticket_id']:
                                        total_amount += float(service['cost'])
                        except Exception as e:
                            print(f"Error calculating total amount: {str(e)}")
                        
                        # Get tax rate and discount from the invoice record
                        try:
                            tax_rate = float(row.get('tax_rate', 0))
                            discount = float(row.get('discount', 0))
                            
                            # Calculate final total with tax and discount
                            tax_amount = total_amount * (tax_rate / 100)
                            final_total = total_amount + tax_amount - discount
                            final_total = max(0, final_total)  # Ensure total is not negative
                            
                            # Format the total amount with 2 decimal places
                            formatted_amount = f"₹{final_total:.2f}"
                        except Exception as e:
                            print(f"Error calculating final total: {str(e)}")
                            formatted_amount = f"₹{total_amount:.2f}"
                        
                        # Get the actual paid status from the invoice record
                        paid_status = row['paid_status']
                        
                        self.invoice_tree.insert('', 'end', values=(
                            row['invoice_id'],
                            f"Ticket #{row['ticket_id']}",
                            ticket_info['customer'],
                            formatted_amount,
                            paid_status,
                            row['date']
                        ))
                    except Exception as e:
                        print(f"Error processing invoice row: {str(e)}")
                        continue
                        
        except FileNotFoundError:
            pass
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load invoices: {str(e)}")

    def delete_invoice(self):
        """Delete the selected invoice"""
        selected_item = self.invoice_tree.selection()
        if not selected_item:
            return
        
        invoice_id = self.invoice_tree.item(selected_item[0])['values'][0]
        invoice_info = f"Invoice #{invoice_id}"
        
        # Confirm deletion
        if not messagebox.askyesno("Confirm Deletion", 
            f"Are you sure you want to delete {invoice_info}?"):
            return
        
        try:
            # Delete invoice
            invoices = []
            with open('data/invoices.csv', 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row['invoice_id'] != invoice_id:
                        invoices.append(row)
            
            with open('data/invoices.csv', 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=['invoice_id', 'ticket_id', 'total_amount', 'paid_status', 'date', 'tax_rate', 'discount'])
                writer.writeheader()
                writer.writerows(invoices)
            
            # Delete PDF file if it exists
            pdf_file = f"invoices/invoice_{invoice_id}.pdf"
            if os.path.exists(pdf_file):
                os.remove(pdf_file)
            
            # Refresh invoice list
            self.load_invoices()
            messagebox.showinfo("Success", f"{invoice_info} has been deleted.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete invoice: {str(e)}")
    
    def show_invoice_menu(self, event):
        """Show the right-click menu for invoice status updates"""
        item = self.invoice_tree.identify_row(event.y)
        if item:
            self.invoice_tree.selection_set(item)
            self.invoice_menu.post(event.x_root, event.y_root)
    
    def update_invoice_status(self, new_status):
        """Update the payment status of a selected invoice"""
        selected_item = self.invoice_tree.selection()
        if not selected_item:
            return
        
        invoice_id = self.invoice_tree.item(selected_item[0])['values'][0]
        
        # Update in CSV
        invoices = []
        try:
            with open('data/invoices.csv', 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row['invoice_id'] == invoice_id:
                        row['paid_status'] = new_status
                    invoices.append(row)
            
            with open('data/invoices.csv', 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=['invoice_id', 'ticket_id', 'total_amount', 'paid_status', 'date', 'tax_rate', 'discount'])
                writer.writeheader()
                writer.writerows(invoices)
            
            # Refresh invoice list
            self.load_invoices()
            messagebox.showinfo("Success", f"Invoice marked as {new_status}")
        except FileNotFoundError:
            messagebox.showerror("Error", "Could not update invoice status")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update invoice status: {str(e)}")
    
    def show_debug_info(self):
        """Show debug information about the current state"""
        try:
            debug_info = []
            
            # Check files
            debug_info.append("File Status:")
            debug_info.append(f"tickets.csv exists: {os.path.exists('data/tickets.csv')}")
            debug_info.append(f"invoices.csv exists: {os.path.exists('data/invoices.csv')}")
            debug_info.append(f"devices.csv exists: {os.path.exists('data/devices.csv')}")
            debug_info.append(f"customers.csv exists: {os.path.exists('data/customers.csv')}")
            
            # Count tickets
            if os.path.exists('data/tickets.csv'):
                with open('data/tickets.csv', 'r') as f:
                    reader = csv.DictReader(f)
                    tickets = list(reader)
                    completed = sum(1 for t in tickets if t['status'] == 'Completed')
                    debug_info.append(f"\nTicket Counts:")
                    debug_info.append(f"Total tickets: {len(tickets)}")
                    debug_info.append(f"Completed tickets: {completed}")
            
            # Count invoices
            if os.path.exists('data/invoices.csv'):
                with open('data/invoices.csv', 'r') as f:
                    reader = csv.DictReader(f)
                    invoices = list(reader)
                    debug_info.append(f"\nInvoice Counts:")
                    debug_info.append(f"Total invoices: {len(invoices)}")
            
            # Show debug info
            messagebox.showinfo("Debug Information", "\n".join(debug_info))
            
        except Exception as e:
            messagebox.showerror("Debug Error", f"Error showing debug info: {str(e)}")

    def create_summary_tab(self):
        """Create the summary tab with statistics and overview"""
        summary_frame = ttk.Frame(self.notebook)
        self.notebook.add(summary_frame, text='Summary')
        
        # Create a frame for statistics
        stats_frame = ttk.LabelFrame(summary_frame, text="Statistics")
        stats_frame.pack(fill='x', padx=5, pady=5)
        
        # Create labels for statistics
        self.total_customers_var = tk.StringVar(value="Total Customers: 0")
        self.total_devices_var = tk.StringVar(value="Total Devices: 0")
        self.total_tickets_var = tk.StringVar(value="Total Tickets: 0")
        self.completed_tickets_var = tk.StringVar(value="Completed Tickets: 0")
        self.total_invoices_var = tk.StringVar(value="Total Invoices: 0")
        self.total_revenue_var = tk.StringVar(value="Total Revenue: ₹0.00")
        
        # Add labels to frame
        ttk.Label(stats_frame, textvariable=self.total_customers_var, font=('Helvetica', 10, 'bold')).pack(pady=5)
        ttk.Label(stats_frame, textvariable=self.total_devices_var, font=('Helvetica', 10, 'bold')).pack(pady=5)
        ttk.Label(stats_frame, textvariable=self.total_tickets_var, font=('Helvetica', 10, 'bold')).pack(pady=5)
        ttk.Label(stats_frame, textvariable=self.completed_tickets_var, font=('Helvetica', 10, 'bold')).pack(pady=5)
        ttk.Label(stats_frame, textvariable=self.total_invoices_var, font=('Helvetica', 10, 'bold')).pack(pady=5)
        ttk.Label(stats_frame, textvariable=self.total_revenue_var, font=('Helvetica', 10, 'bold')).pack(pady=5)
        
        # Add refresh button
        ttk.Button(stats_frame, text="Refresh Statistics", command=self.update_summary_stats).pack(pady=10)
        
        # Update statistics initially
        self.update_summary_stats()

    def update_summary_stats(self):
        """Update the summary statistics"""
        try:
            # Count customers
            total_customers = 0
            if os.path.exists('data/customers.csv'):
                with open('data/customers.csv', 'r') as f:
                    total_customers = len(list(csv.DictReader(f)))
            self.total_customers_var.set(f"Total Customers: {total_customers}")
            
            # Count devices
            total_devices = 0
            if os.path.exists('data/devices.csv'):
                with open('data/devices.csv', 'r') as f:
                    total_devices = len(list(csv.DictReader(f)))
            self.total_devices_var.set(f"Total Devices: {total_devices}")
            
            # Count tickets
            total_tickets = 0
            completed_tickets = 0
            if os.path.exists('data/tickets.csv'):
                with open('data/tickets.csv', 'r') as f:
                    tickets = list(csv.DictReader(f))
                    total_tickets = len(tickets)
                    completed_tickets = sum(1 for t in tickets if t['status'] == 'Completed')
            self.total_tickets_var.set(f"Total Tickets: {total_tickets}")
            self.completed_tickets_var.set(f"Completed Tickets: {completed_tickets}")
            
            # Count invoices and calculate revenue
            total_invoices = 0
            total_revenue = 0.0
            if os.path.exists('data/invoices.csv'):
                with open('data/invoices.csv', 'r') as f:
                    invoices = list(csv.DictReader(f))
                    total_invoices = len(invoices)
                    
                    # Calculate total revenue from services
                    for invoice in invoices:
                        try:
                            with open('data/services.csv', 'r') as s:
                                services = csv.DictReader(s)
                                for service in services:
                                    if service['ticket_id'] == invoice['ticket_id']:
                                        total_revenue += float(service['cost'])
                        except Exception as e:
                            print(f"Error calculating revenue: {str(e)}")
            
            self.total_invoices_var.set(f"Total Invoices: {total_invoices}")
            self.total_revenue_var.set(f"Total Revenue: ₹{total_revenue:.2f}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update statistics: {str(e)}")

    def add_service(self):
        """Add a new service to a ticket"""
        # Get values from form
        ticket = self.service_ticket_var.get().strip()
        description = self.service_desc.get("1.0", tk.END).strip()
        cost = self.service_cost.get().strip()
        
        # Validate required fields
        if not ticket or not description or not cost:
            messagebox.showerror("Error", "All fields are required!")
            return
        
        try:
            # Extract ticket ID from the combo box selection
            ticket_id = ticket.split("Ticket #")[1].split(" -")[0]
            
            # Validate cost is a number
            try:
                cost = float(cost)
            except ValueError:
                messagebox.showerror("Error", "Cost must be a valid number!")
                return
            
            # Add service to CSV
            with open('data/services.csv', 'a', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=['ticket_id', 'description', 'cost'])
                writer.writerow({
                    'ticket_id': ticket_id,
                    'description': description,
                    'cost': cost
                })
            
            # Clear form and refresh list
            self.clear_service_form()
            self.load_services()
            
            messagebox.showinfo("Success", "Service has been added.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add service: {str(e)}")

    def clear_service_form(self):
        """Clear the service form fields"""
        self.service_ticket_var.set('')
        self.service_desc.delete("1.0", tk.END)
        self.service_cost.delete(0, tk.END)

    def load_services(self):
        """Load services from CSV into the treeview"""
        # Clear existing items
        for item in self.service_tree.get_children():
            self.service_tree.delete(item)
        
        # Load from CSV
        try:
            with open('data/services.csv', 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Get ticket info
                    ticket_info = self.get_ticket_info(row['ticket_id'])
                    
                    self.service_tree.insert('', 'end', values=(
                        f"Ticket #{row['ticket_id']}",
                        ticket_info['device'],
                        ticket_info['customer'],
                        row['description'],
                        f"₹{float(row['cost']):.2f}"
                    ))
        except FileNotFoundError:
            pass
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load services: {str(e)}")

    def load_service_ticket_combo(self):
        """Load tickets into the combo box for service creation"""
        try:
            tickets = []
            with open('data/tickets.csv', 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Get device and customer info
                    device_info = self.get_device_info(row['device_id'])
                    customer_name = self.get_customer_name(device_info['customer_id'])
                    
                    tickets.append(f"Ticket #{row['ticket_id']} - {device_info['brand']} {device_info['model']} ({customer_name})")
            self.service_ticket_combo['values'] = tickets
        except FileNotFoundError:
            self.service_ticket_combo['values'] = []
        except Exception as e:
            print(f"Error loading service ticket combo: {str(e)}")
            self.service_ticket_combo['values'] = []

    def generate_invoice(self):
        """Generate an invoice for a completed ticket"""
        # Get values from form
        ticket = self.invoice_ticket_var.get().strip()
        tax_rate = self.tax_rate.get().strip()
        discount = self.discount.get().strip()
        payment_status = self.payment_status_var.get()
        
        # Validate required fields
        if not ticket:
            messagebox.showerror("Error", "Please select a ticket!")
            return
        
        try:
            # Extract ticket ID from the combo box selection
            ticket_id = ticket.split("Ticket #")[1].split(" -")[0]
            
            # Debug information
            debug_info = []
            debug_info.append(f"Selected Ticket ID: {ticket_id}")
            
            # Validate tax rate and discount are numbers
            try:
                tax_rate = float(tax_rate)
                discount = float(discount)
            except ValueError:
                messagebox.showerror("Error", "Tax rate and discount must be valid numbers!")
                return
            
            # Calculate total amount from services
            total_amount = 0
            services_list = []
            
            # Check if services.csv exists
            if not os.path.exists('data/services.csv'):
                messagebox.showerror("Error", "Services file not found! Please add services first.")
                return
                
            try:
                with open('data/services.csv', 'r') as f:
                    reader = csv.DictReader(f)
                    services = list(reader)
                    debug_info.append(f"Total services in file: {len(services)}")
                    
                    for row in reader:
                        if row['ticket_id'] == ticket_id:
                            service_cost = float(row['cost'])
                            total_amount += service_cost
                            services_list.append({
                                'description': row['description'],
                                'cost': service_cost
                            })
                            debug_info.append(f"Found service: {row['description']} - ₹{service_cost}")
            except FileNotFoundError:
                messagebox.showerror("Error", "Services file not found! Please add services first.")
                return
            except Exception as e:
                messagebox.showerror("Error", f"Failed to calculate services total: {str(e)}")
                return
            
            if total_amount == 0:
                # Show debug information
                debug_message = "No services found for this ticket!\n\nDebug Information:\n" + "\n".join(debug_info)
                messagebox.showerror("Error", debug_message)
                return
            
            # Calculate tax and final total
            tax_amount = total_amount * (tax_rate / 100)
            final_total = total_amount + tax_amount - discount
            final_total = max(0, final_total)  # Ensure total is not negative
            
            # Generate new invoice ID
            invoice_id = "1"
            if os.path.exists('data/invoices.csv'):
                with open('data/invoices.csv', 'r') as f:
                    reader = csv.DictReader(f)
                    invoices = list(reader)
                    if invoices:
                        invoice_id = str(int(invoices[-1]['invoice_id']) + 1)
            
            # Get current date
            current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Add invoice to CSV
            with open('data/invoices.csv', 'a', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=['invoice_id', 'ticket_id', 'total_amount', 'paid_status', 'date', 'tax_rate', 'discount'])
                writer.writerow({
                    'invoice_id': invoice_id,
                    'ticket_id': ticket_id,
                    'total_amount': str(final_total),  # Convert to string to ensure proper storage
                    'paid_status': payment_status,
                    'date': current_date,
                    'tax_rate': str(tax_rate),
                    'discount': str(discount)
                })
            
            # Generate PDF invoice
            self.generate_invoice_pdf(invoice_id, ticket_id, final_total, tax_rate, discount, payment_status, current_date, services_list)
            
            # Clear form and refresh list
            self.clear_invoice_form()
            self.load_invoices()
            
            messagebox.showinfo("Success", f"Invoice #{invoice_id} has been generated.\nTotal Amount: ₹{final_total:.2f}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate invoice: {str(e)}")

    def generate_invoice_pdf(self, invoice_id, ticket_id, total_amount, tax_rate, discount, payment_status, date, services_list):
        """Generate a PDF invoice"""
        try:
            # Get ticket info
            ticket_info = self.get_ticket_info(ticket_id)
            
            # Create PDF file
            pdf_file = f"invoices/invoice_{invoice_id}.pdf"
            doc = SimpleDocTemplate(pdf_file, pagesize=letter)
            elements = []
            
            # Add title
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                alignment=TA_CENTER,
                spaceAfter=30
            )
            elements.append(Paragraph(f"Invoice #{invoice_id}", title_style))
            
            # Add customer and device info
            info_style = ParagraphStyle(
                'Info',
                parent=styles['Normal'],
                spaceAfter=12
            )
            elements.append(Paragraph(f"Customer: {ticket_info['customer']}", info_style))
            elements.append(Paragraph(f"Device: {ticket_info['device']}", info_style))
            elements.append(Paragraph(f"Date: {date}", info_style))
            elements.append(Paragraph(f"Payment Status: {payment_status}", info_style))
            
            # Add services table
            services_data = [['Description', 'Cost']]
            
            # Add services from the list
            subtotal = 0
            for service in services_list:
                services_data.append([service['description'], f"₹{service['cost']:.2f}"])
                subtotal += service['cost']
            
            # Calculate tax and total
            tax_amount = subtotal * (tax_rate / 100)
            final_total = subtotal + tax_amount - discount
            
            # Add summary rows
            services_data.append(['Subtotal', f"₹{subtotal:.2f}"])
            services_data.append(['Tax', f"₹{tax_amount:.2f}"])
            services_data.append(['Discount', f"-₹{discount:.2f}"])
            services_data.append(['Total', f"₹{final_total:.2f}"])
            
            # Create table
            table = Table(services_data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, -4), (-1, -1), colors.beige),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(table)
            
            # Build PDF
            doc.build(elements)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate PDF invoice: {str(e)}")

if __name__ == '__main__':
    root = tk.Tk()
    app = RepairCenterApp(root)
    root.mainloop() 