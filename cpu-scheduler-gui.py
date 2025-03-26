import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
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

def fcfs(processes):
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

class CPUSchedulerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("CPU Scheduling Simulator")
        
        self.process_entries = []
        self.algorithm_var = tk.StringVar()
        self.algorithm_var.set("FCFS")
        
        self.setup_ui()
    
    def setup_ui(self):
        # Main title
        tk.Label(self.root, text="CPU Scheduling Simulator", font=('Arial', 14, 'bold')).pack(pady=10)
        
        # Create frame for process entries
        self.entry_frame = tk.Frame(self.root)
        self.entry_frame.pack(padx=20, pady=10)
        
        # Column headers
        headers = ['PID', 'Arrival Time', 'Burst Time', 'Priority']
        for col, header in enumerate(headers):
            tk.Label(self.entry_frame, text=header, font=('Arial', 10, 'bold')).grid(row=0, column=col+1, padx=5, pady=5)
        
        # Process rows
        self.process_entries = []
        for row in range(4):
            # Process label
            tk.Label(self.entry_frame, text=f"Process {row + 1}:", font=('Arial', 10)).grid(row=row+1, column=0, padx=5, pady=5)
            
            # Entry fields
            process_row = []
            for col in range(4):
                entry = tk.Entry(self.entry_frame, width=10)
                entry.grid(row=row+1, column=col+1, padx=5, pady=5)
                process_row.append(entry)
            self.process_entries.append(process_row)
        
        # Algorithm selection
        algorithm_frame = tk.Frame(self.root)
        algorithm_frame.pack(pady=10)
        tk.Label(algorithm_frame, text="Select Algorithm:").pack(side="left", padx=5)
        ttk.Combobox(algorithm_frame, textvariable=self.algorithm_var, 
                    values=["FCFS", "SJF (Non-Preemptive)", "SJF (Preemptive)", "Round Robin", "Priority"]).pack(side="left", padx=5)
        
        # Time Quantum input for Round Robin
        quantum_frame = tk.Frame(self.root)
        quantum_frame.pack(pady=10)
        tk.Label(quantum_frame, text="Time Quantum (RR):").pack(side="left", padx=5)
        self.time_quantum_entry = tk.Entry(quantum_frame, width=10)
        self.time_quantum_entry.pack(side="left", padx=5)
        
        # Start button
        tk.Button(self.root, text="Start Simulation", command=self.start_simulation,
                 font=('Arial', 10, 'bold')).pack(pady=10)
    
    def start_simulation(self):
        processes = []
        for row in self.process_entries:
            values = [entry.get() for entry in row]
            if all(values):
                pid, arrival, burst, priority = map(int, values)
                processes.append(Process(pid, arrival, burst, priority))
        
        algorithm = self.algorithm_var.get()
        
        if algorithm == "FCFS":
            schedule, completed = fcfs(processes)
        elif algorithm == "SJF (Non-Preemptive)":
            schedule, completed = sjf_non_preemptive(processes)
        elif algorithm == "SJF (Preemptive)":
            schedule, completed = preemptive_sjf(processes)
        elif algorithm == "Round Robin":
            time_quantum = int(self.time_quantum_entry.get()) if self.time_quantum_entry.get() else 1
            schedule, completed = round_robin(processes, time_quantum)
        elif algorithm == "Priority":
            schedule, completed = priority_scheduling(processes)
        else:
            return
        
        self.display_results(schedule, completed)
    
    def display_results(self, schedule, processes):
        result_window = tk.Toplevel(self.root)
        result_window.title("Simulation Results")
        
        fig, ax = plt.subplots()
        for i, (pid, start, end) in enumerate(schedule):
            ax.broken_barh([(start, end - start)], (i * 10, 9), facecolors='tab:blue')
            ax.text(start + (end - start) / 2, i * 10 + 5, f"P{pid}", ha='center', va='center', color='white')
        
        ax.set_xlabel("Time")
        ax.set_yticks([])
        ax.set_title("Gantt Chart")
        
        canvas = FigureCanvasTkAgg(fig, master=result_window)
        canvas.draw()
        canvas.get_tk_widget().pack()

if __name__ == "__main__":
    root = tk.Tk()
    app = CPUSchedulerGUI(root)
    root.mainloop()
