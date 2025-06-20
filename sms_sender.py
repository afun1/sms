import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import pandas as pd
import os
from dotenv import load_dotenv
from twilio.rest import Client
import time
import threading
from datetime import datetime
import re
from slybroadcast_rvm import SlybroadcastRVM

class SMSSenderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sparky Messaging - SMS + RVM Platform")
        self.root.geometry("800x700")
        self.root.resizable(True, True)
        
        # Load environment variables
        load_dotenv()
          # Initialize variables
        self.csv_file_path = tk.StringVar()
        self.default_message = tk.StringVar()
        self.default_rvm_message = tk.StringVar()
        self.delay_between_messages = tk.IntVar(value=2)
        self.send_sms = tk.BooleanVar(value=True)
        self.send_rvm = tk.BooleanVar(value=False)
        self.sending_in_progress = False
        
        # Twilio client (will be initialized when credentials are validated)
        self.twilio_client = None
        
        # RVM client
        self.rvm_client = SlybroadcastRVM()
        
        self.setup_ui()
        self.load_credentials()
    
    def setup_ui(self):
        # Create main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
          # Title
        title_label = ttk.Label(main_frame, text="Sparky Messaging", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
          # Credentials Section
        cred_frame = ttk.LabelFrame(main_frame, text="Service Credentials", padding="10")
        cred_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        cred_frame.columnconfigure(1, weight=1)
        
        # Twilio credentials
        ttk.Label(cred_frame, text="Twilio Account SID:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.account_sid_entry = ttk.Entry(cred_frame, width=50)
        self.account_sid_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 5))
        
        ttk.Label(cred_frame, text="Twilio Auth Token:").grid(row=1, column=0, sticky=tk.W, padx=(0, 5), pady=(5, 0))
        self.auth_token_entry = ttk.Entry(cred_frame, show="*", width=50)
        self.auth_token_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(0, 5), pady=(5, 0))
        
        ttk.Label(cred_frame, text="Twilio Phone Number:").grid(row=2, column=0, sticky=tk.W, padx=(0, 5), pady=(5, 0))
        self.phone_number_entry = ttk.Entry(cred_frame, width=50)
        self.phone_number_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(0, 5), pady=(5, 0))
        
        # Slybroadcast credentials
        ttk.Label(cred_frame, text="Slybroadcast Email:").grid(row=3, column=0, sticky=tk.W, padx=(0, 5), pady=(5, 0))
        self.sly_email_entry = ttk.Entry(cred_frame, width=50)
        self.sly_email_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), padx=(0, 5), pady=(5, 0))
        
        ttk.Label(cred_frame, text="Slybroadcast Password:").grid(row=4, column=0, sticky=tk.W, padx=(0, 5), pady=(5, 0))
        self.sly_password_entry = ttk.Entry(cred_frame, show="*", width=50)
        self.sly_password_entry.grid(row=4, column=1, sticky=(tk.W, tk.E), padx=(0, 5), pady=(5, 0))
        
        self.validate_btn = ttk.Button(cred_frame, text="Validate Credentials", 
                                      command=self.validate_credentials)
        self.validate_btn.grid(row=0, column=2, rowspan=5, padx=(5, 0))
        
        # CSV File Selection
        csv_frame = ttk.LabelFrame(main_frame, text="CSV File Selection", padding="10")
        csv_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        csv_frame.columnconfigure(1, weight=1)
        
        ttk.Label(csv_frame, text="CSV File:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.csv_path_entry = ttk.Entry(csv_frame, textvariable=self.csv_file_path, 
                                       state="readonly", width=50)
        self.csv_path_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 5))
        
        ttk.Button(csv_frame, text="Browse", command=self.browse_csv_file).grid(row=0, column=2, padx=(5, 0))
          # Message Configuration
        msg_frame = ttk.LabelFrame(main_frame, text="Message Configuration", padding="10")
        msg_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        msg_frame.columnconfigure(0, weight=1)
        
        # Channel selection
        channel_frame = ttk.Frame(msg_frame)
        channel_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(channel_frame, text="Send Channels:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky=tk.W)
        ttk.Checkbutton(channel_frame, text="SMS Messages", variable=self.send_sms).grid(row=0, column=1, padx=(20, 10))
        ttk.Checkbutton(channel_frame, text="Ringless Voicemail (RVM)", variable=self.send_rvm).grid(row=0, column=2, padx=(10, 0))
        
        # SMS Message
        ttk.Label(msg_frame, text="SMS Message (used when CSV message is empty):").grid(row=1, column=0, sticky=tk.W, pady=(10, 5))
        self.message_text = scrolledtext.ScrolledText(msg_frame, height=3, width=70)
        self.message_text.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # RVM Message
        ttk.Label(msg_frame, text="RVM Message (converted to speech):").grid(row=3, column=0, sticky=tk.W, pady=(10, 5))
        self.rvm_message_text = scrolledtext.ScrolledText(msg_frame, height=3, width=70)
        self.rvm_message_text.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # Placeholders info
        placeholder_info = ttk.Label(msg_frame, text="Available placeholders: {name} - recipient's name", 
                                   font=("Arial", 9), foreground="gray")
        placeholder_info.grid(row=5, column=0, sticky=tk.W)
        
        # Sending Options
        options_frame = ttk.LabelFrame(main_frame, text="Sending Options", padding="10")
        options_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(options_frame, text="Delay between messages (seconds):").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        delay_spinbox = ttk.Spinbox(options_frame, from_=1, to=10, width=5, textvariable=self.delay_between_messages)
        delay_spinbox.grid(row=0, column=1, sticky=tk.W)
        
        # Preview and Send Section
        action_frame = ttk.Frame(main_frame)
        action_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        action_frame.columnconfigure(0, weight=1)
        action_frame.columnconfigure(1, weight=1)
        
        self.preview_btn = ttk.Button(action_frame, text="Preview Messages", 
                                     command=self.preview_messages)
        self.preview_btn.grid(row=0, column=0, padx=(0, 5), sticky=(tk.W, tk.E))
        
        self.send_btn = ttk.Button(action_frame, text="Send SMS Messages", 
                                  command=self.start_sending, style="Accent.TButton")
        self.send_btn.grid(row=0, column=1, padx=(5, 0), sticky=(tk.W, tk.E))
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, 
                                           maximum=100, length=400)
        self.progress_bar.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Status/Log area
        log_frame = ttk.LabelFrame(main_frame, text="Status Log", padding="10")
        log_frame.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(7, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=10, width=70)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))        # Set default messages
        self.message_text.insert("1.0", "Hello {name}, this is a message from our system. Reply STOP to opt out.")
        self.rvm_message_text.insert("1.0", "Hi {name}, this is a voice message from our system. Please check your text messages for more details.")
    
    def load_credentials(self):
        """Load credentials from environment variables"""
        # Twilio credentials
        account_sid = os.getenv('TWILIO_ACCOUNT_SID', '')
        auth_token = os.getenv('TWILIO_AUTH_TOKEN', '')
        phone_number = os.getenv('TWILIO_PHONE_NUMBER', '')
        
        self.account_sid_entry.insert(0, account_sid)
        self.auth_token_entry.insert(0, auth_token)
        self.phone_number_entry.insert(0, phone_number)
        
        # Slybroadcast credentials
        sly_email = os.getenv('SLYBROADCAST_EMAIL', '')
        sly_password = os.getenv('SLYBROADCAST_PASSWORD', '')
        
        self.sly_email_entry.insert(0, sly_email)
        self.sly_password_entry.insert(0, sly_password)        
        if account_sid and auth_token and phone_number:
            self.validate_credentials()
    
    def log_message(self, message):
        """Add a message to the log with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def validate_credentials(self):
        """Validate SMS and RVM credentials"""
        sms_valid = False
        rvm_valid = False
        
        # Validate Twilio credentials
        account_sid = self.account_sid_entry.get().strip()
        auth_token = self.auth_token_entry.get().strip()
        phone_number = self.phone_number_entry.get().strip()
        
        if account_sid and auth_token and phone_number:
            try:
                client = Client(account_sid, auth_token)
                account = client.api.accounts(account_sid).fetch()
                
                self.twilio_client = client
                self.log_message(f"✅ Twilio validated: {account.friendly_name}")
                sms_valid = True
                
            except Exception as e:
                self.log_message(f"❌ Twilio validation failed: {str(e)}")
        
        # Validate Slybroadcast credentials
        sly_email = self.sly_email_entry.get().strip()
        sly_password = self.sly_password_entry.get().strip()
        
        if sly_email and sly_password:
            # Update RVM client credentials
            self.rvm_client.email = sly_email
            self.rvm_client.password = sly_password
            
            if self.rvm_client.is_configured():
                self.log_message(f"✅ Slybroadcast configured: {sly_email}")
                rvm_valid = True
            else:
                self.log_message(f"❌ Slybroadcast configuration failed")
        
        # Show validation results
        if sms_valid and rvm_valid:
            messagebox.showinfo("Success", "Both SMS and RVM credentials validated successfully!")
        elif sms_valid:
            messagebox.showinfo("Partial Success", "SMS credentials validated. RVM credentials needed for voicemail features.")
        elif rvm_valid:
            messagebox.showinfo("Partial Success", "RVM credentials validated. SMS credentials needed for text messaging.")
        else:
            messagebox.showerror("Validation Error", "Please configure at least one service (SMS or RVM)")
    
    def browse_csv_file(self):
        """Open file dialog to select CSV file"""
        file_path = filedialog.askopenfilename(
            title="Select CSV File",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if file_path:
            self.csv_file_path.set(file_path)
            self.log_message(f"Selected CSV file: {file_path}")
            self.validate_csv_file(file_path)
    
    def validate_csv_file(self, file_path):
        """Validate the selected CSV file"""
        try:
            df = pd.read_csv(file_path)
            
            # Check required columns
            required_columns = ['phone_number']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                messagebox.showerror("CSV Error", 
                                   f"Missing required columns: {', '.join(missing_columns)}")
                return False
            
            # Validate phone numbers
            invalid_numbers = []
            for idx, phone in enumerate(df['phone_number']):
                if not self.validate_phone_number(str(phone)):
                    invalid_numbers.append(f"Row {idx + 2}: {phone}")
            
            if invalid_numbers:
                messagebox.showwarning("Phone Number Warning", 
                                     f"Found {len(invalid_numbers)} invalid phone numbers:\n" +
                                     "\n".join(invalid_numbers[:5]) +
                                     ("\n..." if len(invalid_numbers) > 5 else ""))
            
            self.log_message(f"✓ CSV file validated: {len(df)} contacts found")
            return True
            
        except Exception as e:
            self.log_message(f"✗ CSV validation failed: {str(e)}")
            messagebox.showerror("CSV Error", f"Failed to read CSV file:\n{str(e)}")
            return False
    
    def validate_phone_number(self, phone):
        """Basic phone number validation"""
        # Remove all non-digit characters except +
        clean_phone = re.sub(r'[^\d+]', '', str(phone))
        
        # Check if it starts with + and has 10-15 digits
        pattern = r'^\+\d{10,15}$'
        return bool(re.match(pattern, clean_phone))
    
    def preview_messages(self):
        """Preview messages that would be sent"""
        if not self.csv_file_path.get():
            messagebox.showerror("Error", "Please select a CSV file first")
            return
        
        try:
            df = pd.read_csv(self.csv_file_path.get())
            default_msg = self.message_text.get("1.0", tk.END).strip()
            
            preview_window = tk.Toplevel(self.root)
            preview_window.title("Message Preview")
            preview_window.geometry("600x400")
            
            preview_text = scrolledtext.ScrolledText(preview_window, wrap=tk.WORD)
            preview_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            for idx, row in df.head(10).iterrows():  # Show first 10 for preview
                phone = row['phone_number']
                name = row.get('name', 'Friend')
                custom_msg = row.get('message', '')
                
                # Use custom message if available, otherwise use default
                message = custom_msg if custom_msg and str(custom_msg).strip() else default_msg
                
                # Replace placeholders
                if name and str(name).strip() and str(name) != 'nan':
                    message = message.replace('{name}', str(name))
                else:
                    message = message.replace('{name}', 'Friend')
                
                preview_text.insert(tk.END, f"To: {phone}\nMessage: {message}\n{'-'*50}\n")
            
            if len(df) > 10:
                preview_text.insert(tk.END, f"\n... and {len(df) - 10} more messages")
            
            preview_text.config(state=tk.DISABLED)
            
        except Exception as e:
            messagebox.showerror("Preview Error", f"Failed to generate preview:\n{str(e)}")
    
    def start_sending(self):
        """Start the SMS sending process in a separate thread"""
        if self.sending_in_progress:
            messagebox.showwarning("Warning", "Sending already in progress!")
            return
        
        if not self.twilio_client:
            messagebox.showerror("Error", "Please validate Twilio credentials first")
            return
        
        if not self.csv_file_path.get():
            messagebox.showerror("Error", "Please select a CSV file first")
            return
        
        # Confirm sending
        if not messagebox.askyesno("Confirm", "Are you sure you want to send SMS messages to all contacts?"):
            return
        
        # Disable send button and start sending
        self.send_btn.config(state=tk.DISABLED)
        self.sending_in_progress = True
        
        # Start sending in a separate thread
        thread = threading.Thread(target=self.send_messages)
        thread.daemon = True
        thread.start()
    
    def send_messages(self):
        """Send SMS messages to all contacts in the CSV"""
        try:
            df = pd.read_csv(self.csv_file_path.get())
            default_msg = self.message_text.get("1.0", tk.END).strip()
            total_messages = len(df)
            
            self.log_message(f"Starting to send {total_messages} messages...")
            
            successful_sends = 0
            failed_sends = 0
            
            for idx, row in df.iterrows():
                try:
                    phone = str(row['phone_number']).strip()
                    name = row.get('name', 'Friend')
                    custom_msg = row.get('message', '')
                    
                    # Validate phone number
                    if not self.validate_phone_number(phone):
                        self.log_message(f"✗ Skipping invalid phone number: {phone}")
                        failed_sends += 1
                        continue
                    
                    # Prepare message
                    message = custom_msg if custom_msg and str(custom_msg).strip() and str(custom_msg) != 'nan' else default_msg
                    
                    # Replace placeholders
                    if name and str(name).strip() and str(name) != 'nan':
                        message = message.replace('{name}', str(name))
                    else:
                        message = message.replace('{name}', 'Friend')
                    
                    # Send SMS
                    message_instance = self.twilio_client.messages.create(
                        body=message,
                        from_=self.phone_number_entry.get().strip(),
                        to=phone
                    )
                    
                    self.log_message(f"✓ Sent to {phone} (SID: {message_instance.sid})")
                    successful_sends += 1
                    
                except Exception as e:
                    self.log_message(f"✗ Failed to send to {phone}: {str(e)}")
                    failed_sends += 1
                
                # Update progress
                progress = ((idx + 1) / total_messages) * 100
                self.progress_var.set(progress)
                
                # Delay between messages
                if idx < total_messages - 1:  # Don't delay after the last message
                    time.sleep(self.delay_between_messages.get())
            
            # Final summary
            self.log_message(f"✓ Sending completed! Success: {successful_sends}, Failed: {failed_sends}")
            
            if successful_sends > 0:
                messagebox.showinfo("Success", 
                                  f"Sending completed!\nSuccessful: {successful_sends}\nFailed: {failed_sends}")
            else:
                messagebox.showerror("Error", "No messages were sent successfully")
            
        except Exception as e:
            self.log_message(f"✗ Sending process failed: {str(e)}")
            messagebox.showerror("Error", f"Sending process failed:\n{str(e)}")
        
        finally:
            # Re-enable send button and reset progress
            self.send_btn.config(state=tk.NORMAL)
            self.sending_in_progress = False
            self.progress_var.set(0)

def main():
    root = tk.Tk()
    app = SMSSenderApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
