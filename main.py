import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import socket
import subprocess
import threading
import platform
from datetime import datetime


class NetworkTracker:

    def __init__(self, root):
        self.root = root
        self.root.title("All-in-One Network Tracker")
        self.root.geometry("950x700")
        self.root.minsize(750, 580)
        self.root.configure(bg="#101827")

        self.results = []
        self.busy = False

        self.setup_styles()
        self.create_interface()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "TButton",
            font=("Segoe UI", 10),
            padding=9
        )

        style.configure(
            "TEntry",
            padding=9,
            font=("Segoe UI", 12)
        )

        style.configure(
            "TLabel",
            background="#101827",
            foreground="white",
            font=("Segoe UI", 10)
        )

    def create_interface(self):

        # Header
        header = tk.Frame(self.root, bg="#17243a", pady=20)
        header.pack(fill="x")

        tk.Label(
            header,
            text="NETWORK TRACKER",
            font=("Segoe UI", 23, "bold"),
            bg="#17243a",
            fg="#38bdf8"
        ).pack()

        tk.Label(
            header,
            text="IP ADDRESS | PING | TRACEROUTE",
            font=("Segoe UI", 10),
            bg="#17243a",
            fg="#cbd5e1"
        ).pack(pady=5)

        # Main container
        main = tk.Frame(self.root, bg="#101827", padx=25, pady=20)
        main.pack(fill="both", expand=True)

        tk.Label(
            main,
            text="Enter Website or IP Address",
            font=("Segoe UI", 12, "bold"),
            bg="#101827",
            fg="white"
        ).pack(anchor="w")

        self.host_entry = ttk.Entry(main)
        self.host_entry.pack(fill="x", pady=10)
        self.host_entry.insert(0, "google.com")

        # Buttons
        button_frame = tk.Frame(main, bg="#101827")
        button_frame.pack(fill="x", pady=10)

        self.ip_button = ttk.Button(
            button_frame,
            text="Find IP Address",
            command=self.find_ip
        )
        self.ip_button.pack(side="left", expand=True, fill="x", padx=4)

        self.ping_button = ttk.Button(
            button_frame,
            text="Ping Test",
            command=self.ping_test
        )
        self.ping_button.pack(side="left", expand=True, fill="x", padx=4)

        self.trace_button = ttk.Button(
            button_frame,
            text="Traceroute",
            command=self.traceroute
        )
        self.trace_button.pack(side="left", expand=True, fill="x", padx=4)

        # Status
        self.status = tk.Label(
            main,
            text="Ready",
            font=("Segoe UI", 10, "bold"),
            bg="#101827",
            fg="#4ade80"
        )
        self.status.pack(anchor="w", pady=8)

        self.progress = ttk.Progressbar(
            main,
            mode="indeterminate"
        )
        self.progress.pack(fill="x", pady=5)

        # Results heading
        tk.Label(
            main,
            text="NETWORK RESULTS",
            font=("Segoe UI", 12, "bold"),
            bg="#101827",
            fg="#38bdf8"
        ).pack(anchor="w", pady=(15, 5))

        # Output box
        output_frame = tk.Frame(main, bg="#101827")
        output_frame.pack(fill="both", expand=True)

        self.output = tk.Text(
            output_frame,
            bg="#0b1220",
            fg="#d1e7ff",
            insertbackground="white",
            font=("Consolas", 10),
            wrap="word",
            padx=12,
            pady=12,
            relief="flat"
        )

        scrollbar = ttk.Scrollbar(
            output_frame,
            command=self.output.yview
        )

        self.output.configure(
            yscrollcommand=scrollbar.set
        )

        self.output.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.output.insert(
            "end",
            "Welcome to All-in-One Network Tracker!\n\n"
            "Enter a website or IP address above.\n"
            "Select a tool to begin network testing.\n"
        )

        # Bottom buttons
        bottom = tk.Frame(main, bg="#101827")
        bottom.pack(fill="x", pady=12)

        ttk.Button(
            bottom,
            text="Export Report",
            command=self.export_report
        ).pack(side="left", padx=4)

        ttk.Button(
            bottom,
            text="Clear Results",
            command=self.clear_results
        ).pack(side="left", padx=4)

        self.buttons = [
            self.ip_button,
            self.ping_button,
            self.trace_button
        ]

    def get_host(self):

        host = self.host_entry.get().strip()

        if not host:
            messagebox.showwarning(
                "Missing Input",
                "Please enter a website or IP address."
            )
            return None

        if any(c.isspace() for c in host):
            messagebox.showwarning(
                "Invalid Input",
                "Please enter a valid hostname or IP address."
            )
            return None

        return host

    def add_output(self, text):

        self.output.insert("end", text + "\n")
        self.output.see("end")

        self.results.append(text)

    def run_task(self, title, function):

        if self.busy:
            return

        self.busy = True

        for button in self.buttons:
            button.config(state="disabled")

        self.status.config(
            text=title + " in progress...",
            fg="#facc15"
        )

        self.progress.start(10)

        def worker():

            try:
                result = function()
            except Exception as error:
                result = f"An error occurred: {error}"

            self.root.after(
                0,
                lambda: self.finish_task(title, result)
            )

        threading.Thread(
            target=worker,
            daemon=True
        ).start()

    def finish_task(self, title, result):

        self.progress.stop()

        self.add_output("\n" + "=" * 55)
        self.add_output(title)
        self.add_output("=" * 55)
        self.add_output(result)

        self.busy = False

        for button in self.buttons:
            button.config(state="normal")

        self.status.config(
            text="Task completed",
            fg="#4ade80"
        )

    # IP ADDRESS FINDER
    def find_ip(self):

        host = self.get_host()

        if not host:
            return

        def task():

            try:
                addresses = socket.getaddrinfo(
                    host,
                    None,
                    socket.AF_INET,
                    socket.SOCK_STREAM
                )

                ips = sorted({
                    item[4][0] for item in addresses
                })

                if not ips:
                    return "No IPv4 address found."

                return (
                    f"Website: {host}\n"
                    f"IPv4 Address(es):\n" +
                    "\n".join(ips) +
                    f"\nLookup Time: {datetime.now()}"
                )

            except socket.gaierror:
                return (
                    "Unable to find the IP address.\n"
                    "Check the website name or internet connection."
                )

        self.run_task("IP Address Lookup", task)

    # PING TEST
    def ping_test(self):

        host = self.get_host()

        if not host:
            return

        def task():

            if platform.system().lower() != "windows":
                return "This version is designed for Windows."

            command = [
                "ping",
                "-n", "4",
                "-w", "2000",
                host
            ]

            try:
                result = subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    timeout=15
                )

                status = (
                    "Reachable"
                    if result.returncode == 0
                    else "Unreachable or no replies received"
                )

                return (
                    f"Target: {host}\n"
                    f"Status: {status}\n\n"
                    f"{result.stdout}"
                )

            except subprocess.TimeoutExpired:
                return "Ping test timed out."

            except FileNotFoundError:
                return "Windows ping utility was not found."

        self.run_task("Ping Test", task)

    # TRACEROUTE
    def traceroute(self):

        host = self.get_host()

        if not host:
            return

        def task():

            if platform.system().lower() != "windows":
                return "This version is designed for Windows."

            command = [
                "tracert",
                "-d",
                "-h", "20",
                "-w", "1000",
                host
            ]

            try:
                result = subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    timeout=60
                )

                return (
                    f"Target: {host}\n"
                    f"Traceroute Output:\n\n"
                    f"{result.stdout}\n"
                    f"{result.stderr}"
                )

            except subprocess.TimeoutExpired:
                return "Traceroute timed out."

            except FileNotFoundError:
                return "Windows tracert utility was not found."

        self.run_task("Traceroute", task)

    # EXPORT REPORT
    def export_report(self):

        content = self.output.get("1.0", "end-1c")

        if not content.strip():
            messagebox.showwarning(
                "Empty Report",
                "There are no results to export."
            )
            return

        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt")],
            initialfile="Network_Report.txt"
        )

        if filename:

            with open(filename, "w", encoding="utf-8") as file:
                file.write("ALL-IN-ONE NETWORK TRACKER REPORT\n")
                file.write("=" * 45 + "\n")
                file.write(
                    "Generated: " +
                    str(datetime.now()) +
                    "\n\n"
                )
                file.write(content)

            messagebox.showinfo(
                "Success",
                "Network report exported successfully!"
            )

    # CLEAR RESULTS
    def clear_results(self):

        if self.busy:
            return

        self.output.delete("1.0", "end")
        self.results.clear()

        self.status.config(
            text="Ready",
            fg="#4ade80"
        )


# START APPLICATION
if __name__ == "__main__":

    root = tk.Tk()

    app = NetworkTracker(root)

    root.mainloop()
