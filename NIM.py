import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider

# Constants
SAFE_COLOR = "seagreen"  # Green for safe positions
UNSAFE_COLOR = "tomato"  # Red for unsafe positions
DEFAULT_COLOR = "royalblue"  # Blue for heaps

INITIAL_HEAPS = [1, 3, 5, 7]  # Initial heap sizes
MAX_HEAP_SIZE = max(INITIAL_HEAPS)  # Maximum heap size for sliders

# UI Layout Constants
FIG_SIZE_HEAP = (8, 8)  # Figure size for heap visualization
FIG_SIZE_TABLE = (8, 6)  # Figure size for the information table
BOTTOM_ADJUST = 0.1  # Space at the bottom for UI elements
HEAP_SPACING = 2  # Horizontal spacing between heap positions
CIRCLE_RADIUS = 0.4  # Radius of heap circles
NIM_SUM_MIN_BITS = 4  # Ensure at least 4-bit binary representation

# Slider Layout Constants
SLIDER_WIDTH = 0.6
SLIDER_HEIGHT = 0.03
SLIDER_START_X = 0.2
SLIDER_START_Y = 0.08
SLIDER_SPACING = 0.05  # Vertical space between sliders

# Table Layout Constants
TABLE_BBOX = [0, 0.5, 1, 0.5]  # Position of the table
TABLE_FONT_SIZE = 10
COLUMN_WIDTHS = [0.1, 0.1, 0.15, 0.05, 0.15, 0.05, 0.15, 0.1, 0.15]  # Column width ratios

class NimGame:
    def __init__(self, heaps):
        self.heaps = heaps
        self.nim_val = 0
        self.binary_heaps = []
        self.binary_nim_val = ""
        self.xor_equation = ""
        self.heaps_changed = True  # Flag to track if heaps have changed

        self.fig, self.ax = plt.subplots(figsize=FIG_SIZE_HEAP)
        self.fig_info, self.ax_info = plt.subplots(figsize=FIG_SIZE_TABLE)
        self.fig.canvas.manager.set_window_title("🔵 Heap Visualization 🔵")
        self.fig_info.canvas.manager.set_window_title("🧮 Mathematical Insights 🧮")
        self.sliders = []
        
        self.setup_ui()

    def compute_nim_sum(self):
        """Compute the nim-sum and store it to avoid redundant calculations."""
        if self.heaps_changed:
            max_bits = max(NIM_SUM_MIN_BITS, max(self.heaps).bit_length())
            self.binary_heaps = [bin(h)[2:].zfill(max_bits) for h in self.heaps]
            self.nim_val = np.bitwise_xor.reduce(self.heaps)
            self.binary_nim_val = bin(self.nim_val)[2:].zfill(max_bits)
            self.xor_equation = " ⊕ ".join(self.binary_heaps) + f" = {self.binary_nim_val}"
            self.heaps_changed = False

    def setup_ui(self):
        """Set up the UI, including sliders and initial plot."""
        plt.subplots_adjust(bottom=BOTTOM_ADJUST)
        self.ax_info.axis("off")
        self.plot_nim()
        self.create_sliders()

    def setup_axes(self):
        """Set up axes properties for the heap plot."""
        self.ax.clear()
        self.ax.set_xlim(-1, len(self.heaps) * HEAP_SPACING)
        self.ax.set_ylim(-0.5, MAX_HEAP_SIZE)
        self.ax.set_xticks(range(0, len(self.heaps) * HEAP_SPACING, HEAP_SPACING))
        self.ax.set_xticklabels([f"Heap {i+1}" for i in range(len(self.heaps))])
        self.ax.set_yticks([])
        self.ax.set_facecolor('#F5F5F5')
        self.ax.set_aspect('auto')

    def generate_table_data(self):
        """Generate data for the table using stored Nim-sum values."""
        xor_results = [h ^ self.nim_val for h in self.heaps]

        table_data = [
            [
                f"Heap {i+1}",
                h,
                self.binary_heaps[i],
                "⊕",
                self.binary_nim_val,
                "=",
                bin(xor_results[i])[2:].zfill(len(self.binary_nim_val)),
                xor_results[i],
                "YES" if xor_results[i] < h else "NO"
            ]
            for i, h in enumerate(self.heaps)
        ]
    
        # Add the Nim-sum row at the bottom
        table_data.append([
            "Nim-Sum *", self.nim_val, self.binary_nim_val, "", "", "", "", "", ""
        ])
    
        return table_data

    def draw_heap_circles(self):
        """Draw circles representing the heaps."""
        for i, h in enumerate(self.heaps):
            for j in range(h):
                self.ax.add_patch(plt.Circle((i * HEAP_SPACING, j), CIRCLE_RADIUS, color=DEFAULT_COLOR))

    def update_table(self):
        """Update the table using stored Nim-sum values."""
        self.ax_info.clear()
        self.ax_info.axis("off")

        table_data = self.generate_table_data()
        column_labels = ["Heap#", "Dec", "Bin", "", "Nim-Sum", "", "Bin'", "Dec'", "Safe Move?"]

        # Create and format table
        table = self.ax_info.table(cellText=table_data, colLabels=column_labels, cellLoc="center", loc="center", bbox=TABLE_BBOX)
        table.auto_set_font_size(False)
        table.set_fontsize(TABLE_FONT_SIZE)

        # Adjust column widths
        for i, width in enumerate(COLUMN_WIDTHS):                            
            table.auto_set_column_width(i)
            table.get_celld()[(0, i)].set_width(width)

        # Make header labels bold
        for (row, col), cell in table.get_celld().items():
            if row == 0:  # Header row
                cell.get_text().set_weight("bold")

        # Change cell colors for "Safe Move?"
        for row in range(1, len(table_data)):  
            cell = table.get_celld()[(row, 8)]
            cell.set_facecolor(SAFE_COLOR if table_data[row-1][8] == "YES" else UNSAFE_COLOR)

        # Change cell color and weight for "Dec'" column based on "Safe Move?"
        for row in range(1, len(table_data)):  
            safe_move = table_data[row-1][8] == "YES"
            color = SAFE_COLOR if safe_move else UNSAFE_COLOR
            cell = table.get_celld()[(row, 7)]
            cell.get_text().set_weight("bold")
            cell.get_text().set_color(color)

        # Make the Nim-sum row bold
        for col in range(len(column_labels)):
            cell = table.get_celld()[(len(table_data), col)]
            cell.get_text().set_weight("bold")

        # Display XOR equation below the table
        self.ax_info.text(0.5, 0.44, f"*Nim-Sum = Bitwise XOR of All Heap Sizes: {self.xor_equation}",
                          fontsize=10, ha="center", weight="normal", family="monospace")

        # Explanation of XOR (⊕) symbol
        self.ax_info.text(0.5, 0.35, "Note: ⊕ represents the bitwise XOR operation, which compares binary digits \n"
                                     "and returns 1 if they are different and 0 if they are the same.",
                          fontsize=9, ha="center", weight="normal", family="monospace")

    def plot_nim(self):
        """Update the entire UI without redundant Nim-sum calculations."""
        self.compute_nim_sum()  # Recalculate only when needed
        self.setup_axes()
        self.ax.set_title(f"Nim-Sum = {self.nim_val} ({self.binary_nim_val}) ({'Safe' if self.nim_val == 0 else 'Unsafe'})",
                          fontsize=14, color=SAFE_COLOR if self.nim_val == 0 else UNSAFE_COLOR)

        self.draw_heap_circles()
        self.update_table()
        self.fig.canvas.draw_idle()
        self.fig_info.canvas.draw_idle()

    def create_sliders(self):
        """Create sliders for heap size adjustment."""
        for i in range(len(self.heaps)):
            ax_slider = plt.axes([SLIDER_START_X, SLIDER_START_Y + (len(self.heaps) - i - 1) * SLIDER_SPACING, SLIDER_WIDTH, SLIDER_HEIGHT])
            slider = Slider(ax_slider, f"Heap {i+1}", 0, MAX_HEAP_SIZE, valinit=self.heaps[i], valstep=1)
            slider.on_changed(self.update)
            self.sliders.append(slider)

    def update(self, val):
        """Callback for slider updates."""
        self.heaps = [int(slider.val) for slider in self.sliders]
        self.heaps_changed = True  # Set flag to indicate heaps have changed
        self.plot_nim()

# Initialize and run the Nim game
if __name__ == "__main__":
    nim_game = NimGame(INITIAL_HEAPS)
    plt.show(block=True)
