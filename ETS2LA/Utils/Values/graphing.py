import matplotlib.pyplot as plt
from collections import deque
import time

class PIDGraph:
    def __init__(self, history=10):
        """
        Initialize a real-time PID graph display
        
        Parameters:
        history (float): Time window to display in seconds
        
        Please remember to call setup_plot() before using the graph.
        """
        self.history = history
        
        # Initialize data structures with deques (efficient fixed-size queues)
        self.times = deque(maxlen=500)  # Store timestamp data
        self.setpoints = deque(maxlen=500)  # Store setpoint values
        self.outputs = deque(maxlen=500)  # Store controller output values
        self.p_terms = deque(maxlen=500)  # Store proportional terms
        self.i_terms = deque(maxlen=500)  # Store integral terms
        self.d_terms = deque(maxlen=500)  # Store derivative terms
        
        # Record start time for relative time tracking
        self.start_time = time.time()
        
    def setup_plot(self):
        """Configure the plot layout and styling"""
        plt.ion()  # Enable interactive mode
        
        # Create figure and subplots
        self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(10, 8))
        self.fig.tight_layout(pad=3.0)
        
        # Configure main PID plot
        self.ax1.set_title('PID Control')
        self.ax1.set_xlabel('Time (s)')
        self.ax1.set_ylabel('Value')
        self.ax1.grid(True)
        
        # Configure components plot
        self.ax2.set_title('PID Components')
        self.ax2.set_xlabel('Time (s)')
        self.ax2.set_ylabel('Value')
        self.ax2.grid(True)
        
        # Initialize empty lines for the plots
        self.setpoint_line, = self.ax1.plot([], [], 'r-', label='Setpoint')
        self.output_line, = self.ax1.plot([], [], 'b-', label='Output')
        self.p_term_line, = self.ax2.plot([], [], 'g-', label='P-term')
        self.i_term_line, = self.ax2.plot([], [], 'y-', label='I-term')
        self.d_term_line, = self.ax2.plot([], [], 'c-', label='D-term')
        
        # Add legends
        self.ax1.legend(loc='upper right')
        self.ax2.legend(loc='upper right')
        
        # Show the plot
        plt.show(block=False)
        
    def update(self, setpoint, output, p_term, i_term, d_term):
        """
        Update the graph with new PID values
        
        Parameters:
        setpoint (float): Target value
        output (float): Controller output value
        p_term (float): Proportional term
        i_term (float): Integral term
        d_term (float): Derivative term
        """
        # Get current time
        current_time = time.time() - self.start_time
        
        # Add data to deques
        self.times.append(current_time)
        self.setpoints.append(setpoint)
        self.outputs.append(output)
        self.p_terms.append(p_term)
        self.i_terms.append(i_term)
        self.d_terms.append(d_term)
        
        # Update x-axis limits to show the last history seconds
        if current_time > self.history:
            self.ax1.set_xlim(current_time - self.history, current_time)
            self.ax2.set_xlim(current_time - self.history, current_time)
        else:
            self.ax1.set_xlim(0, self.history)
            self.ax2.set_xlim(0, self.history)
            
        # Update plot data
        times_list = list(self.times)
        self.setpoint_line.set_data(times_list, self.setpoints)
        self.output_line.set_data(times_list, self.outputs)
        self.p_term_line.set_data(times_list, self.p_terms)
        self.i_term_line.set_data(times_list, self.i_terms)
        self.d_term_line.set_data(times_list, self.d_terms)
        
        # Adjust y-axis limits as needed
        self.ax1.relim()
        self.ax1.autoscale_view()
        self.ax2.relim()
        self.ax2.autoscale_view()
        
        # Draw the updated plots
        self.fig.canvas.draw_idle()
        self.fig.canvas.flush_events()
        
    def clear(self):
        """Clear all data from the graph"""
        self.times.clear()
        self.setpoints.clear()
        self.outputs.clear()
        self.p_terms.clear()
        self.i_terms.clear()
        self.d_terms.clear()
        
        # Reset the start time
        self.start_time = time.time()
        
    def close(self):
        """Close the plot window"""
        plt.close(self.fig)