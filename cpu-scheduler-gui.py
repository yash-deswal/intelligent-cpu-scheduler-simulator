import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import random
import csv
from collections import deque


# Dummy Process class (replace with your actual implementation)
class Process:
    def __init__(self, pid, arrival_time, burst_time, priority=0):
        self.pid = pid
        self.arrival_time = arrival_time
        self.burst_time = burst_time
        self.priority = priority
        self.remaining_time = burst_time
        self.start_time = -1
        self.completion_time = 0
        self.waiting_time = 0
        self.turnaround_time = 0
        self.response_time = -1


# Dummy Scheduling Algorithms (replace with your actual implementations)
def fcfs_scheduling(processes):
    processes.sort(key=lambda x: x.arrival_time)
    current_time = 0
    schedule = []
    
    for process in processes:
        if current_time < process.arrival_time:
            current_time = process.arrival_time
        process.start_time = current_time
        process.completion_time = current_time + process.burst_time
        process.turnaround_time = process.completion_time - process.arrival_time
        process.waiting_time = process.turnaround_time - process.burst_time
        process.response_time = process.start_time - process.arrival_time
        schedule.append((process.pid, process.start_time, process.completion_time))
        current_time += process.burst_time
    
    return schedule, processes


def sjf_non_preemptive(processes):
    processes.sort(key=lambda x: (x.arrival_time, x.burst_time))
    current_time = 0
    schedule = []
    completed = []
    
    while processes:
        available = [p for p in processes if p.arrival_time <= current_time]
        if available:
            process = min(available, key=lambda x: x.burst_time)
            processes.remove(process)
            process.start_time = current_time
            process.completion_time = current_time + process.burst_time
            process.turnaround_time = process.completion_time - process.arrival_time
            process.waiting_time = process.turnaround_time - process.burst_time
            schedule.append((process.pid, process.start_time, process.completion_time))
            current_time += process.burst_time
            completed.append(process)
        else:
            current_time += 1
    
    return schedule, completed


def round_robin(processes, time_quantum):
    queue = deque()
    schedule = []
    current_time = 0
    processes.sort(key=lambda x: x.arrival_time)
    index = 0
    
    while index < len(processes) or queue:
        while index < len(processes) and processes[index].arrival_time <= current_time:
            queue.append(processes[index])
            index += 1
        if queue:
            process = queue.popleft()
            if process.response_time == -1:
                process.response_time = current_time - process.arrival_time
            execution_time = min(time_quantum, process.remaining_time)
            process.remaining_time -= execution_time
            schedule.append((process.pid, current_time, current_time + execution_time))
            current_time += execution_time
            if process.remaining_time > 0:
                queue.append(process)
            else:
                process.completion_time = current_time
                process.turnaround_time = process.completion_time - process.arrival_time
                process.waiting_time = process.turnaround_time - process.burst_time
        else:
            current_time += 1
    
    return schedule, processes


def priority_scheduling(processes):
    current_time = 0
    schedule = []
    completed = []
    remaining_processes = processes.copy()
    
    while remaining_processes:
        available = [p for p in remaining_processes if p.arrival_time <= current_time]
        if available:
            # Select process with highest priority (lower number means higher priority)
            process = min(available, key=lambda x: x.priority)
            remaining_processes.remove(process)
            
            process.start_time = current_time
            process.completion_time = current_time + process.burst_time
            process.turnaround_time = process.completion_time - process.arrival_time
            process.waiting_time = process.turnaround_time - process.burst_time
            process.response_time = process.start_time - process.arrival_time
            
            schedule.append((process.pid, process.start_time, process.completion_time))
            current_time += process.burst_time
            completed.append(process)
        else:
            current_time += 1
    
    return schedule, completed

def preemptive_sjf(processes):
    current_time = 0
    schedule = []
    completed = []
    remaining_processes = [Process(p.pid, p.arrival_time, p.burst_time, p.priority) for p in processes]
    current_process = None
    last_process = None
    
    while remaining_processes or current_process:
        # Update available processes
        available = [p for p in remaining_processes if p.arrival_time <= current_time]
        
        if not available and not current_process:
            current_time += 1
            continue
            
        # Find process with shortest remaining time
        if available:
            shortest_process = min(available, key=lambda x: x.remaining_time)
            if not current_process or shortest_process.remaining_time < current_process.remaining_time:
                if current_process:
                    remaining_processes.append(current_process)
                current_process = shortest_process
                remaining_processes.remove(shortest_process)
                
                # If process changed, add to schedule
                if current_process != last_process:
                    if last_process and schedule:
                        schedule[-1] = (last_process.pid, schedule[-1][1], current_time)
                    schedule.append((current_process.pid, current_time, None))
                    if current_process.response_time == -1:
                        current_process.response_time = current_time - current_process.arrival_time
        
        # Execute current process
        if current_process:
            current_process.remaining_time -= 1
            if current_process.remaining_time == 0:
                current_process.completion_time = current_time + 1
                current_process.turnaround_time = current_process.completion_time - current_process.arrival_time
                current_process.waiting_time = current_process.turnaround_time - current_process.burst_time
                completed.append(current_process)
                schedule[-1] = (current_process.pid, schedule[-1][1], current_time + 1)
                last_process = None
                current_process = None
            else:
                last_process = current_process
                
        current_time += 1
    
    return schedule, completed


class SchedulerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Intelligent CPU Scheduler Simulator")
        self.root.configure(bg="#1e1e1e")  # Dark theme background
        self.process_list = []

        # Style Configuration
        style = ttk.Style()
        style.theme_use("clam")  # Modern look
        style.configure("TButton", font=("Arial", 10, "bold"), padding=6, background="#007BFF", foreground="white")
        style.map("TButton", background=[("active", "#0056b3")])
        style.configure("TCombobox", padding=5, fieldbackground="white", background="white")

        # Heading
        title_label = tk.Label(root, text="Intelligent CPU Scheduler Simulator", font=("Arial", 16, "bold"), fg="white", bg="#1e1e1e")
        title_label.grid(row=0, column=0, columnspan=6, pady=10)

        # Input Fields
        ttk.Label(root, text="PID", foreground="white", background="#1e1e1e").grid(row=1, column=0)
        ttk.Label(root, text="Arrival", foreground="white", background="#1e1e1e").grid(row=1, column=1)
        ttk.Label(root, text="Burst", foreground="white", background="#1e1e1e").grid(row=1, column=2)
        ttk.Label(root, text="Priority", foreground="white", background="#1e1e1e").grid(row=1, column=3)

        self.pid_entry = ttk.Entry(root, width=10)
        self.arrival_entry = ttk.Entry(root, width=10)
        self.burst_entry = ttk.Entry(root, width=10)
        self.priority_entry = ttk.Entry(root, width=10)
        self.pid_entry.grid(row=2, column=0, padx=5)
        self.arrival_entry.grid(row=2, column=1, padx=5)
        self.burst_entry.grid(row=2, column=2, padx=5)
        self.priority_entry.grid(row=2, column=3, padx=5)

        self.add_button = ttk.Button(root, text="Add Process", command=self.add_process)
        self.add_button.grid(row=2, column=4, padx=5)

        # Dropdown for algorithm selection
        self.algo_var = tk.StringVar()
        self.algo_dropdown = ttk.Combobox(root, textvariable=self.algo_var, values=["FCFS", "SJF", "Round Robin", "Priority"], state="readonly")
        self.algo_dropdown.grid(row=3, column=0, columnspan=2, pady=5)
        self.algo_dropdown.set("FCFS")

        # Time Quantum Input for Round Robin
        ttk.Label(root, text="Time Quantum", foreground="white", background="#1e1e1e").grid(row=3, column=2)
        self.quantum_entry = ttk.Entry(root, width=10)
        self.quantum_entry.grid(row=3, column=3, padx=5)

        # Buttons
        self.run_button = ttk.Button(root, text="Run", command=self.run_scheduler)
        self.run_button.grid(row=3, column=4, pady=5)

        self.reset_button = ttk.Button(root, text="Reset", command=self.reset_scheduler)
        self.reset_button.grid(row=3, column=5, pady=5)

        # Animation Speed Control
        ttk.Label(root, text="Animation Speed", foreground="white", background="#1e1e1e").grid(row=6, column=0)
        self.speed_scale = ttk.Scale(root, from_=1, to=100, orient="horizontal")
        self.speed_scale.set(15)  # Default speed
        self.speed_scale.grid(row=6, column=1, columnspan=4, pady=5)

        # Export Results Button
        self.export_button = ttk.Button(root, text="Export Results", command=self.export_results)
        self.export_button.grid(row=6, column=5, pady=5)

        # Table with Styling
        self.tree = ttk.Treeview(root, columns=("PID", "Arrival", "Burst", "Priority", "Waiting", "Turnaround", "Completion", "Response"), show="headings", height=8)
        for col in ("PID", "Arrival", "Burst", "Priority", "Waiting", "Turnaround", "Completion", "Response"):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=90, anchor="center")

        self.tree.grid(row=4, column=0, columnspan=6, pady=10, padx=10)

        # Table Styling (Alternating Row Colors)
        self.tree.tag_configure("oddrow", background="#2b2b2b", foreground="white")
        self.tree.tag_configure("evenrow", background="#3b3b3b", foreground="white")

        # Canvas for animation (Black Background)
        self.canvas = tk.Canvas(root, width=700, height=150, bg="black", highlightthickness=2, highlightbackground="white")
        self.canvas.grid(row=5, column=0, columnspan=6, pady=10)

    def add_process(self):
        try:
            pid = int(self.pid_entry.get())
            arrival = int(self.arrival_entry.get())
            burst = int(self.burst_entry.get())
            priority = int(self.priority_entry.get())

            # Check for duplicate PID
            if any(p.pid == pid for p in self.process_list):
                messagebox.showerror("Duplicate PID", "A process with this PID already exists.")
                return

            process = Process(pid, arrival, burst, priority)
            self.process_list.append(process)
            tag = "evenrow" if len(self.process_list) % 2 == 0 else "oddrow"
            self.tree.insert("", "end", values=(pid, arrival, burst, priority, 0, 0, 0, 0), tags=(tag,))
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid integer values!")

    def run_scheduler(self):
        algo = self.algo_var.get()
        if not self.process_list:
            messagebox.showerror("No Processes", "Please add at least one process before running the scheduler.")
            return

        try:
            if algo == "FCFS":
                scheduled_processes = fcfs_scheduling(self.process_list)
            elif algo == "SJF":
                scheduled_processes = sjf_scheduling(self.process_list)
            elif algo == "Round Robin":
                try:
                    quantum = int(self.quantum_entry.get())
                    if quantum <= 0:
                        raise ValueError("Time quantum must be a positive integer.")
                    scheduled_processes = round_robin_scheduling(self.process_list, quantum)
                except ValueError as e:
                    messagebox.showerror("Invalid Time Quantum", str(e))
                    return
            elif algo == "Priority":
                scheduled_processes = priority_scheduling(self.process_list)
            else:
                messagebox.showerror("Invalid Algorithm", "Selected algorithm is not supported.")
                return
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while running the scheduler: {str(e)}")
            return

        # Clear the table and update with new results
        self.tree.delete(*self.tree.get_children())
        schedule = []
        start_time = 0

        for p in scheduled_processes:
            completion_time = start_time + p.burst
            response_time = p.waiting_time  
            tag = "evenrow" if len(schedule) % 2 == 0 else "oddrow"
            self.tree.insert("", "end", values=(p.pid, p.arrival, p.burst, p.priority, p.waiting_time, p.turnaround_time, completion_time, response_time), tags=(tag,))
            schedule.append({"pid": p.pid, "start": start_time, "duration": p.burst, "completion": completion_time})
            start_time += p.burst

        self.animate_execution(schedule)

    def reset_scheduler(self):
        """Resets all process data and clears the canvas."""
        self.process_list.clear()
        self.tree.delete(*self.tree.get_children())
        self.canvas.delete("all")

    def animate_execution(self, schedule):
        """Animates the Gantt chart execution process."""
        self.canvas.delete("all")
        start_x = 20

        for i, process in enumerate(schedule):
            process_width = process["duration"] * 30
            color = random.choice(["#ff6b6b", "#feca57", "#1dd1a1", "#5f27cd", "#54a0ff"])

            rect = self.canvas.create_rectangle(start_x, 40, start_x, 80, fill=color, outline="white")
            for step in range(process_width):
                self.canvas.coords(rect, start_x, 40, start_x + step, 80)
                self.root.update()
                self.root.after(int(self.speed_scale.get()))  # Use the slider value

            text = self.canvas.create_text(start_x + process_width / 2, 60, text=f"P{process['pid']}", font=("Arial", 12, "bold"), fill="white")

            if i == 0 or process["start"] != schedule[i-1]["completion"]:
                self.canvas.create_text(start_x, 100, text=f"{process['start']}", font=("Arial", 10), fill="white")
            self.canvas.create_text(start_x + process_width, 100, text=f"{process['completion']}", font=("Arial", 10), fill="white")

            start_x += process_width

        self.canvas.create_text(350, 120, text="🎉 Execution Completed! 🎉", fill="green", font=("Arial", 14, "bold"))

    def export_results(self):
        """Exports the scheduling results to a CSV file."""
        if not self.process_list:
            messagebox.showerror("No Data", "No processes to export.")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if not file_path:
            return

        with open(file_path, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["PID", "Arrival", "Burst", "Priority", "Waiting", "Turnaround", "Completion", "Response"])
            for process in self.process_list:
                writer.writerow([process.pid, process.arrival, process.burst, process.priority, process.waiting_time, process.turnaround_time, process.completion_time, process.response_time])

        messagebox.showinfo("Export Successful", f"Results exported to {file_path}")


# Run the application
root = tk.Tk()
app = SchedulerGUI(root)
root.mainloop()