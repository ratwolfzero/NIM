import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider

# Constants
SAFE_COLOR = "#008811"  # Green for safe positions
UNSAFE_COLOR = "#D05533"  # Red for unsafe positions
DEFAULT_COLOR = "#4169E1"  # Blue for heaps
INITIAL_HEAPS = [1, 3, 5, 7]  # Initial heap sizes
MAX_HEAP_SIZE = 10  # Maximum heap size for sliders

class NimGame:
    def __init__(self, heaps):
        self.heaps = heaps
        self.fig, self.ax = plt.subplots(figsize=(8, 8))
        self.fig_info, self.ax_info = plt.subplots(figsize=(8, 6))
        self.sliders = []
        self.setup_ui()

    def setup_ui(self):
        """Set up the UI, including sliders and initial plot."""
        plt.subplots_adjust(bottom=0.1)
        self.ax_info.axis("off")
        self.plot_nim()
        self.create_sliders()

    def nim_sum_with_binary(self):
        """Compute the nim-sum and return its binary representation."""
        max_bits = max(4, max(self.heaps).bit_length())  # Ensure at least 4-bit representation
        binary_heaps = [bin(h)[2:].zfill(max_bits) for h in self.heaps]
        nim_val = np.bitwise_xor.reduce(self.heaps)
        binary_nim_val = bin(nim_val)[2:].zfill(max_bits)
        xor_equation = " ⊕ ".join(binary_heaps) + f" = {binary_nim_val}"
        return nim_val, binary_heaps, binary_nim_val, xor_equation

    def setup_axes(self):
        """Set up axes properties for the heap plot."""
        self.ax.clear()
        self.ax.set_xlim(-1, len(self.heaps) * 2)
        self.ax.set_ylim(-0.5, MAX_HEAP_SIZE)
        self.ax.set_xticks(range(0, len(self.heaps) * 2, 2))
        self.ax.set_xticklabels([f"Heap {i+1}" for i in range(len(self.heaps))])
        self.ax.set_yticks([])
        self.ax.set_facecolor('#F5F5F5')
        self.ax.set_aspect('auto')

    def generate_table_data(self, nim_val, binary_heaps, binary_nim_val):
        """Generate data for the table."""
        table_data = [
            [
                f"Heap {i+1}", 
                h, 
                binary_heaps[i], 
                "⊕", 
                binary_nim_val, 
                "=", 
                bin(h ^ nim_val)[2:].zfill(len(binary_nim_val)), 
                h ^ nim_val, 
                "YES" if (h ^ nim_val) < h else "NO"
            ] for i, h in enumerate(self.heaps)
        ]
        
        # Add the Nim-sum row at the bottom
        table_data.append([
            "Nim-Sum *", nim_val, binary_nim_val, "", "", "", "", "", ""
        ])
        
        return table_data

    def draw_heap_circles(self):
        """Draw circles representing the heaps."""
        for i, h in enumerate(self.heaps):
            for j in range(h):
                self.ax.add_patch(plt.Circle((i * 2, j), 0.4, color=DEFAULT_COLOR))

    def update_table(self, nim_val, binary_heaps, binary_nim_val, xor_equation):
        """Update the table with new data."""
        self.ax_info.clear()
        self.ax_info.axis("off")

        table_data = self.generate_table_data(nim_val, binary_heaps, binary_nim_val)
        column_labels = ["Heap#", "Dec", "Bin", "", "Nim-Sum", "", "Bin'", "Dec'", "Safe Move?"]

        # Create and format table
        table = self.ax_info.table(cellText=table_data, colLabels=column_labels, cellLoc="center", loc="center", bbox=[0, 0.5, 1, 0.5])
        table.auto_set_font_size(False)
        table.set_fontsize(10)

        # Adjust column widths
        col_widths = [0.1, 0.1, 0.15, 0.05, 0.15, 0.05, 0.15, 0.1, 0.15]
        for i, width in enumerate(col_widths):                            
            table.auto_set_column_width(i)
            table.get_celld()[(0, i)].set_width(width)

        # Make header labels bold
        for (row, col), cell in table.get_celld().items():
            if row == 0:  # Header row
                cell.get_text().set_weight("bold")

        # Change cell colors for "Safe Move?" (only for heap rows)
        for row in range(1, len(table_data)):  # Iterate over all rows except the Nim-sum row
            cell = table.get_celld()[(row, 8)]
            cell.set_facecolor(SAFE_COLOR if table_data[row-1][8] == "YES" else UNSAFE_COLOR)

        # Make the Nim-sum row bold
        for col in range(len(column_labels)):
            cell = table.get_celld()[(len(table_data), col)]
            cell.get_text().set_weight("bold")

        # Display XOR equation below the table
        self.ax_info.text(0.5, 0.44, f"*Nim-Sum = Bitwise XOR of All Heap Sizes: {xor_equation}",
                          fontsize=10, ha="center", weight="normal", family="monospace")
        
        # Explanation of XOR (⊕) symbol
        self.ax_info.text(0.5, 0.35, "Note: ⊕ represents the bitwise XOR operation, which compares binary digits \n"
                             "and returns 1 if they are different and 0 if they are the same.",
                  fontsize=9, ha="center", weight="normal", family="monospace")

    def plot_nim(self):
        """Update the entire UI."""
        self.setup_axes()
        nim_val, binary_heaps, binary_nim_val, xor_equation = self.nim_sum_with_binary()
        
        # Update title in Figure 1 (heap visualization)
        self.ax.set_title(f"Nim-Sum = {nim_val} ({binary_nim_val}) ({'Safe' if nim_val == 0 else 'Unsafe'})",
                          fontsize=14, color=SAFE_COLOR if nim_val == 0 else UNSAFE_COLOR)
        
        self.draw_heap_circles()
        self.update_table(nim_val, binary_heaps, binary_nim_val, xor_equation)
        self.fig.canvas.draw_idle()
        self.fig_info.canvas.draw_idle()

    def create_sliders(self):
        """Create sliders for heap size adjustment."""
        for i in range(len(self.heaps)):
            ax_slider = plt.axes([0.2, 0.08 + (len(self.heaps) - i - 1) * 0.07, 0.6, 0.03])
            slider = Slider(ax_slider, f"Heap {i+1}", 0, MAX_HEAP_SIZE, valinit=self.heaps[i], valstep=1)
            slider.on_changed(self.update)
            self.sliders.append(slider)

    def update(self, val):
        """Callback for slider updates."""
        self.heaps = [int(slider.val) for slider in self.sliders]
        self.plot_nim()

# Initialize and run the Nim game
nim_game = NimGame(INITIAL_HEAPS)
plt.show(block=True)