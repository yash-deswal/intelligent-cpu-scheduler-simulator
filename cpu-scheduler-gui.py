import tkinter as tk
from tkinter import ttk
import heapq
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
    processes.sort(key=lambda x: x.arrival_time)  # Sort by arrival time
    current_time = 0
    schedule = []

    for process in processes:
        if current_time < process.arrival_time:
            current_time = process.arrival_time  # CPU idle time

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
            current_time += 1  # CPU idle

    return schedule, completed

def sjf_preemptive(processes):
    processes.sort(key=lambda x: x.arrival_time)
    current_time = 0
    schedule = []
    remaining_processes = []
    heapq.heapify(remaining_processes)
    index = 0
    last_pid = None

    while index < len(processes) or remaining_processes:
        while index < len(processes) and processes[index].arrival_time <= current_time:
            heapq.heappush(remaining_processes, (processes[index].burst_time, index))
            index += 1

        if remaining_processes:
            burst_time, idx = heapq.heappop(remaining_processes)
            process = processes[idx]

            if process.response_time == -1:
                process.response_time = current_time - process.arrival_time

            if last_pid != process.pid:
                schedule.append((process.pid, current_time))

            process.remaining_time -= 1
            current_time += 1

            if process.remaining_time > 0:
                heapq.heappush(remaining_processes, (process.remaining_time, idx))
            else:
                process.completion_time = current_time
                process.turnaround_time = process.completion_time - process.arrival_time
                process.waiting_time = process.turnaround_time - process.burst_time
        else:
            current_time += 1

    return schedule, processes

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
            current_time += 1  # CPU idle

    return schedule, processes

def priority_non_preemptive(processes):
    processes.sort(key=lambda x: (x.arrival_time, x.priority))
    current_time = 0
    schedule = []
    completed = []

    while processes:
        available = [p for p in processes if p.arrival_time <= current_time]
        if available:
            process = min(available, key=lambda x: x.priority)
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

class CPUSchedulerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("CPU Scheduling Simulator")

        # Frame for process input
        self.input_frame = tk.Frame(root, padx=10, pady=10)
        self.input_frame.pack(pady=10)

        # Labels and Entry Fields
        tk.Label(self.input_frame, text="Process ID").grid(row=0, column=0)
        tk.Label(self.input_frame, text="Arrival Time").grid(row=0, column=1)
        tk.Label(self.input_frame, text="Burst Time").grid(row=0, column=2)
        tk.Label(self.input_frame, text="Priority").grid(row=0, column=3)

        self.process_entries = []
        for i in range(5):  # Default 5 rows for input
            row_entries = []
            for j in range(4):  # Process ID, Arrival Time, Burst Time, Priority
                entry = tk.Entry(self.input_frame, width=10)
                entry.grid(row=i+1, column=j, padx=5, pady=5)
                row_entries.append(entry)
            self.process_entries.append(row_entries)

        # Algorithm Selection
        tk.Label(root, text="Select Scheduling Algorithm").pack()
        self.algorithm_var = tk.StringVar()
        self.algorithm_dropdown = ttk.Combobox(root, textvariable=self.algorithm_var, values=[
            "FCFS", "SJF (Preemptive)", "SJF (Non-Preemptive)", "Round Robin", "Priority (Preemptive)", "Priority (Non-Preemptive)"
        ])
        self.algorithm_dropdown.pack()

        # Time Quantum (only for Round Robin)
        self.time_quantum_label = tk.Label(root, text="Time Quantum (for RR)")
        self.time_quantum_entry = tk.Entry(root, width=10)

        self.algorithm_dropdown.bind("<<ComboboxSelected>>", self.toggle_time_quantum)

        # Start Button
        self.start_button = tk.Button(root, text="Start Simulation", command=self.start_simulation)
        self.start_button.pack(pady=10)

    def toggle_time_quantum(self, event):
        """ Show/Hide time quantum input based on algorithm selection """
        if "Round Robin" in self.algorithm_var.get():
            self.time_quantum_label.pack()
            self.time_quantum_entry.pack()
        else:
            self.time_quantum_label.pack_forget()
            self.time_quantum_entry.pack_forget()

    def start_simulation(self):
        """ Placeholder function for starting simulation """
        print("Simulation Started with", self.algorithm_var.get())

# Run the GUI
if __name__ == "__main__":
    root = tk.Tk()
    gui = CPUSchedulerGUI(root)
    root.mainloop()