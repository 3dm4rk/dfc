import psutil
import tkinter as tk
from tkinter import ttk
import time
from threading import Thread
import os

class NotificationWindow:
    def __init__(self, root, message):
        self.root = root
        self.notification = tk.Toplevel(root)
        self.notification.overrideredirect(True)  # Remove window decorations
        
        # Calculate position (upper right corner)
        screen_width = self.notification.winfo_screenwidth()
        self.notification.geometry(f"300x100+{screen_width-320}+20")
        
        # Styling
        self.notification.configure(bg='#2c3e50')
        self.notification.attributes('-alpha', 0.9)  # Slightly transparent
        
        # Message
        tk.Label(
            self.notification, 
            text="App Terminated", 
            fg='#ecf0f1', 
            bg='#e74c3c',
            font=('Arial', 12, 'bold'),
            anchor='w',
            padx=10
        ).pack(fill='x')
        
        tk.Label(
            self.notification, 
            text=message, 
            fg='#ecf0f1', 
            bg='#2c3e50',
            font=('Arial', 10),
            padx=10,
            pady=10,
            wraplength=280,
            justify='left'
        ).pack(fill='both', expand=True)
        
        # Close button
        close_btn = tk.Button(
            self.notification, 
            text="×", 
            command=self.notification.destroy,
            bg='#e74c3c',
            fg='white',
            borderwidth=0,
            font=('Arial', 10, 'bold')
        )
        close_btn.place(x=275, y=5, width=20, height=20)
        
        # Auto-close after 5 seconds
        self.notification.after(5000, self.notification.destroy)

class AppMonitor:
    def __init__(self, root):
        self.root = root
        self.root.title("App Terminator Notifier")
        self.root.geometry("400x250")
        self.root.resizable(False, False)
        
        # Styling
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('TFrame', background='#ecf0f1')
        self.style.configure('TLabel', background='#ecf0f1', font=('Arial', 10))
        self.style.configure('TButton', font=('Arial', 10))
        
        # Main frame
        main_frame = ttk.Frame(root, padding="20")
        main_frame.pack(fill='both', expand=True)
        
        # Variables
        self.target_process = tk.StringVar()
        self.monitoring = False
        
        # GUI Elements
        ttk.Label(main_frame, text="Monitor Application Termination", font=('Arial', 12, 'bold')).pack(pady=10)
        
        input_frame = ttk.Frame(main_frame)
        input_frame.pack(fill='x', pady=10)
        
        ttk.Label(input_frame, text="Process Name:").pack(side='left')
        self.process_entry = ttk.Entry(input_frame, textvariable=self.target_process, width=25)
        self.process_entry.pack(side='left', padx=10)
        self.process_entry.focus()
        
        ttk.Label(main_frame, text="Example: chrome.exe, notepad.exe", foreground='gray').pack()
        
        self.status_label = ttk.Label(main_frame, text="Status: Ready", foreground='gray')
        self.status_label.pack(pady=10)
        
        self.monitor_btn = ttk.Button(main_frame, text="Start Monitoring", command=self.toggle_monitoring)
        self.monitor_btn.pack(pady=10)
        
        # System tray icon would go here (requires additional libraries)
    
    def toggle_monitoring(self):
        target = self.target_process.get().strip()
        
        if not target:
            self.show_error("Please enter a process name")
            return
        
        if not self.monitoring:
            if not self.is_process_running(target):
                self.show_error(f"'{target}' is not running")
                return
            
            self.monitoring = True
            self.monitor_btn.config(text="Stop Monitoring")
            self.status_label.config(text=f"Monitoring: {target}", foreground='green')
            Thread(target=self.monitor_process, daemon=True).start()
        else:
            self.monitoring = False
            self.monitor_btn.config(text="Start Monitoring")
            self.status_label.config(text="Status: Ready", foreground='gray')
    
    def is_process_running(self, process_name):
        try:
            return any(proc.info['name'].lower() == process_name.lower() 
                      for proc in psutil.process_iter(['name']))
        except:
            return False
    
    def monitor_process(self):
        target = self.target_process.get().strip().lower()
        
        while self.monitoring:
            if not self.is_process_running(target):
                message = f"{target} was forcefully terminated!"
                self.root.after(0, self.show_notification, message)
                self.root.after(0, lambda: self.status_label.config(
                    text=f"Detected termination: {target}", foreground='red'))
                self.monitoring = False
                self.root.after(0, lambda: self.monitor_btn.config(text="Start Monitoring"))
                break
            time.sleep(1)
    
    def show_notification(self, message):
        NotificationWindow(self.root, message)
    
    def show_error(self, message):
        self.status_label.config(text=f"Error: {message}", foreground='red')

if __name__ == "__main__":
    root = tk.Tk()
    app = AppMonitor(root)
    root.mainloop()
