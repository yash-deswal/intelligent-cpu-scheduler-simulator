import tkinter as tk
from tkinter import ttk

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