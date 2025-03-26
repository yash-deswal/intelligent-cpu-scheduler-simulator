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

class CPUSchedulerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("CPU Scheduling Simulator")
        
        self.process_entries = []
        self.algorithm_var = tk.StringVar()
        self.algorithm_var.set("FCFS")
        
        self.setup_ui()
    
    def setup_ui(self):
        tk.Label(self.root, text="Process Details (PID, Arrival, Burst, Priority)").pack()
        self.entry_frame = tk.Frame(self.root)
        self.entry_frame.pack()
        
        for _ in range(4):
            row = [tk.Entry(self.entry_frame, width=10) for _ in range(4)]
            for entry in row:
                entry.pack(side="left", padx=5)
            self.process_entries.append(row)
        
        tk.Label(self.root, text="Select Algorithm:").pack()
        ttk.Combobox(self.root, textvariable=self.algorithm_var, values=["FCFS", "SJF (Non-Preemptive)", "Round Robin"]).pack()
        
        self.time_quantum_entry = tk.Entry(self.root, width=10)
        tk.Label(self.root, text="Time Quantum (RR)").pack()
        self.time_quantum_entry.pack()
        
        tk.Button(self.root, text="Start Simulation", command=self.start_simulation).pack()
    
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
        elif algorithm == "Round Robin":
            time_quantum = int(self.time_quantum_entry.get()) if self.time_quantum_entry.get() else 1
            schedule, completed = round_robin(processes, time_quantum)
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
