import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import random
import csv
from collections import deque


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
            process.response_time = process.start_time - process.arrival_time
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
        
        available = [p for p in remaining_processes if p.arrival_time <= current_time]
        
        if not available and not current_process:
            current_time += 1
            continue
            
        
        if available:
            shortest_process = min(available, key=lambda x: x.remaining_time)
            if not current_process or shortest_process.remaining_time < current_process.remaining_time:
                if current_process:
                    remaining_processes.append(current_process)
                current_process = shortest_process
                remaining_processes.remove(shortest_process)
                
                # If process changed, update schedule
                if current_process != last_process:
                    if last_process and schedule:
                        schedule[-1] = (last_process.pid, schedule[-1][1], current_time)
                    schedule.append((current_process.pid, current_time, None))
                    if current_process.response_time == -1:
                        current_process.response_time = current_time - current_process.arrival_time
        
        
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
        self.root.title("CPU Scheduler Simulator")
        self.root.configure(bg="#1e1e1e")
        self.process_list = []

        
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TButton", font=("Arial", 10, "bold"), padding=6, background="#007BFF", foreground="white")
        style.map("TButton", background=[("active", "#0056b3")])
        style.configure("TCombobox", padding=5)

        
        tk.Label(root, text="CPU Scheduler Simulator", font=("Arial", 16, "bold"), fg="white", bg="#1e1e1e").grid(row=0, column=0, columnspan=6, pady=10)

       
        tk.Label(root, text="PID", fg="white", bg="#1e1e1e").grid(row=1, column=0)
        tk.Label(root, text="Arrival", fg="white", bg="#1e1e1e").grid(row=1, column=1)
        tk.Label(root, text="Burst", fg="white", bg="#1e1e1e").grid(row=1, column=2)
        tk.Label(root, text="Priority", fg="white", bg="#1e1e1e").grid(row=1, column=3)

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

        
        self.algo_var = tk.StringVar()
        self.algo_dropdown = ttk.Combobox(root, textvariable=self.algo_var, values=["FCFS", "SJF", "Preemptive SJF", "Round Robin", "Priority"], state="readonly")
        self.algo_dropdown.grid(row=3, column=0, columnspan=2, pady=5)
        self.algo_dropdown.set("FCFS")

        
        tk.Label(root, text="Time Quantum", fg="white", bg="#1e1e1e").grid(row=3, column=2)
        self.quantum_entry = ttk.Entry(root, width=10)
        self.quantum_entry.grid(row=3, column=3, padx=5)

        
        self.run_button = ttk.Button(root, text="Run", command=self.run_scheduler)
        self.run_button.grid(row=3, column=4, pady=5)
        self.reset_button = ttk.Button(root, text="Reset", command=self.reset_scheduler)
        self.reset_button.grid(row=3, column=5, pady=5)

        
        tk.Label(root, text="Animation Speed", fg="white", bg="#1e1e1e").grid(row=6, column=0)
        self.speed_scale = ttk.Scale(root, from_=1, to=100, orient="horizontal")
        self.speed_scale.set(15)
        self.speed_scale.grid(row=6, column=1, columnspan=4, pady=5)

       
        self.export_button = ttk.Button(root, text="Export Results", command=self.export_results)
        self.export_button.grid(row=6, column=5, pady=5)

       
        self.tree = ttk.Treeview(root, columns=("PID", "Arrival", "Burst", "Priority", "Waiting", "Turnaround", "Completion", "Response"), show="headings", height=8)
        for col in ("PID", "Arrival", "Burst", "Priority", "Waiting", "Turnaround", "Completion", "Response"):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=90, anchor="center")
        self.tree.grid(row=4, column=0, columnspan=6, pady=10, padx=10)

       
        self.tree.tag_configure("oddrow", background="#2b2b2b", foreground="white")
        self.tree.tag_configure("evenrow", background="#3b3b3b", foreground="white")

        
        self.canvas = tk.Canvas(root, width=700, height=150, bg="black", highlightthickness=2, highlightbackground="white")
        self.canvas.grid(row=5, column=0, columnspan=6, pady=10)

    def add_process(self):
        try:
            pid = int(self.pid_entry.get())
            arrival = int(self.arrival_entry.get())
            burst = int(self.burst_entry.get())
            priority = int(self.priority_entry.get())

            if any(p.pid == pid for p in self.process_list):
                messagebox.showerror("Duplicate PID", "A process with this PID already exists.")
                return

            if burst <= 0 or arrival < 0:
                messagebox.showerror("Invalid Input", "Burst time must be positive, and arrival time must be non-negative.")
                return

            process = Process(pid, arrival, burst, priority)
            self.process_list.append(process)
            tag = "evenrow" if len(self.process_list) % 2 == 0 else "oddrow"
            self.tree.insert("", "end", values=(pid, arrival, burst, priority, 0, 0, 0, 0), tags=(tag,))
            self.pid_entry.delete(0, tk.END)
            self.arrival_entry.delete(0, tk.END)
            self.burst_entry.delete(0, tk.END)
            self.priority_entry.delete(0, tk.END)
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid integer values!")

    def run_scheduler(self):
        algo = self.algo_var.get()
        if not self.process_list:
            messagebox.showerror("No Processes", "Please add at least one process before running the scheduler.")
            return

        try:
            if algo == "FCFS":
                schedule, processes = fcfs_scheduling(self.process_list[:])
            elif algo == "SJF":
                schedule, processes = sjf_non_preemptive(self.process_list[:])
            elif algo == "Preemptive SJF":  # New condition for Preemptive SJF
                schedule, processes = preemptive_sjf(self.process_list[:])
            elif algo == "Round Robin":
                quantum = int(self.quantum_entry.get())
                if quantum <= 0:
                    raise ValueError("Time quantum must be a positive integer.")
                schedule, processes = round_robin(self.process_list[:], quantum)
            elif algo == "Priority":
                schedule, processes = priority_scheduling(self.process_list[:])
            else:
                messagebox.showerror("Invalid Algorithm", "Selected algorithm is not supported.")
                return

            
            self.tree.delete(*self.tree.get_children())
            for idx, p in enumerate(processes):
                tag = "evenrow" if idx % 2 == 0 else "oddrow"
                self.tree.insert("", "end", values=(
                    p.pid, p.arrival_time, p.burst_time, p.priority,
                    p.waiting_time, p.turnaround_time, p.completion_time, p.response_time
                ), tags=(tag,))

            
            self.animate_execution(schedule)

        except ValueError as e:
            messagebox.showerror("Invalid Input", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def reset_scheduler(self):
        self.process_list.clear()
        self.tree.delete(*self.tree.get_children())
        self.canvas.delete("all")
        self.pid_entry.delete(0, tk.END)
        self.arrival_entry.delete(0, tk.END)
        self.burst_entry.delete(0, tk.END)
        self.priority_entry.delete(0, tk.END)
        self.quantum_entry.delete(0, tk.END)

    def animate_execution(self, schedule):
        self.canvas.delete("all")
        scale = 30  # Pixels per time unit
        y_top = 40
        y_bottom = 80
        previous_end = 0

        for pid, start, end in schedule:
            x_start = start * scale
            x_end = end * scale
            duration = end - start
            color = random.choice(["#ff6b6b", "#feca57", "#1dd1a1", "#5f27cd", "#54a0ff"])

            # Animate rectangle growth
            rect = self.canvas.create_rectangle(x_start, y_top, x_start, y_bottom, fill=color, outline="white")
            for step in range(duration):
                current_x = x_start + (step + 1) * scale
                self.canvas.coords(rect, x_start, y_top, current_x, y_bottom)
                self.root.update()
                self.root.after(int(self.speed_scale.get()))

            # Add PID text
            self.canvas.create_text((x_start + x_end) / 2, (y_top + y_bottom) / 2, text=f"P{pid}", font=("Arial", 12, "bold"), fill="white")

            # Add time labels
            if start != previous_end or start == 0:
                self.canvas.create_text(x_start, y_bottom + 20, text=f"{start}", font=("Arial", 10), fill="white")
            self.canvas.create_text(x_end, y_bottom + 20, text=f"{end}", font=("Arial", 10), fill="white")
            previous_end = end

        self.canvas.create_text(350, 120, text="Execution Completed!", fill="green", font=("Arial", 14, "bold"))

    def export_results(self):
        if not self.process_list:
            messagebox.showerror("No Data", "No processes to export.")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if file_path:
            with open(file_path, mode="w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(["PID", "Arrival", "Burst", "Priority", "Waiting", "Turnaround", "Completion", "Response"])
                for p in self.process_list:
                    writer.writerow([p.pid, p.arrival_time, p.burst_time, p.priority, p.waiting_time, p.turnaround_time, p.completion_time, p.response_time])
            messagebox.showinfo("Export Successful", f"Results exported to {file_path}")

# Run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = SchedulerGUI(root)
    root.mainloop()