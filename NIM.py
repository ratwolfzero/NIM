import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider

# Define colors
SAFE_COLOR = "#008811"  # Green for safe positions
UNSAFE_COLOR = "#D05533"  # Red for unsafe positions
DEFAULT_COLOR = "#4169E1"  # Blue for heaps

# Initial heap sizes
heaps = [1, 3, 5, 7]

# Function to compute Nim-sum and return binary representations
def nim_sum_with_binary(heaps):
    max_bits = max(4, max(heaps).bit_length())  # Ensure at least 4-bit representation
    binary_heaps = [bin(h)[2:].zfill(max_bits) for h in heaps]
    nim_val = np.bitwise_xor.reduce(heaps)
    binary_nim_val = bin(nim_val)[2:].zfill(max_bits)
    
    # Create XOR equation string
    xor_equation = " ⊕ ".join(binary_heaps) + f" = {binary_nim_val}"
    
    return nim_val, binary_heaps, binary_nim_val, xor_equation

# Setup axes properties
def setup_axes(ax, num_heaps, max_height):
    ax.clear()
    ax.set_xlim(-1, num_heaps * 2)
    ax.set_ylim(-0.5, max_height)
    ax.set_xticks(range(0, num_heaps * 2, 2))
    ax.set_xticklabels([f"Heap {i+1}" for i in range(num_heaps)])
    ax.set_yticks([])
    ax.set_facecolor('#F5F5F5')
    ax.set_aspect('equal')

# Generate table data
def generate_table_data(heaps, nim_val, binary_heaps, binary_nim_val):
    table_data = []
    for i, h in enumerate(heaps):
        new_h = h ^ nim_val
        binary_new_h = bin(new_h)[2:].zfill(len(binary_nim_val))
        safe_move_possible = "YES" if new_h < h else "NO"
        table_data.append([
            f"Heap {i+1}", h, binary_heaps[i], binary_nim_val, binary_new_h, new_h, safe_move_possible
        ])
    return table_data

# Create main figure
plt.ion()
fig, ax = plt.subplots(figsize=(8, 8))
plt.subplots_adjust(bottom=0.1)
fig_info, ax_info = plt.subplots(figsize=(8, 6))
ax_info.axis("off")

def plot_nim(heaps):
    setup_axes(ax, len(heaps), 10)
    nim_val, binary_heaps, binary_nim_val, xor_equation = nim_sum_with_binary(heaps)

    # Title
    ax.set_title(f"Nim-Sum: {nim_val} ({binary_nim_val}) ({'Safe' if nim_val == 0 else 'Unsafe'})",
                 fontsize=14, color=SAFE_COLOR if nim_val == 0 else UNSAFE_COLOR)

    # Draw heap circles
    for i, h in enumerate(heaps):
        for j in range(h):
            ax.add_patch(plt.Circle((i * 2, j), 0.4, color=DEFAULT_COLOR))

    # Update table in second window
    ax_info.clear()
    ax_info.axis("off")

    table_data = generate_table_data(heaps, nim_val, binary_heaps, binary_nim_val)
    column_labels = ["Heap#", "Dec", "Bin", "⊕ Nim-Sum", "= Bin'", "Dec'", "Safe Move?"]

    # Display XOR equation above table
    ax_info.text(0.5, 1.05, f"Nim-Sum Calculation XOR all Heaps: {xor_equation}",
                 fontsize=12, ha="center", weight="normal", family="monospace")

    # Display Nim-Sum below XOR equation
    ax_info.text(0.5, 1.0, f"Nim-Sum: {nim_val} (Binary: {binary_nim_val})",
                 fontsize=12, ha="center", weight="bold")

    # Create and format table
    table = ax_info.table(cellText=table_data, colLabels=column_labels, cellLoc="center", loc="center", bbox=[0, 0.4, 1, 0.5])
    table.auto_set_font_size(False)
    table.set_fontsize(10)

    # Change cell colors for "Safe Move?"
    for (row, col), cell in table.get_celld().items():
        if col == 6 and row > 0:
            cell.set_facecolor(SAFE_COLOR if table_data[row-1][col] == "YES" else UNSAFE_COLOR)
            cell.get_text().set_weight("bold")

    fig.canvas.draw_idle()
    fig_info.canvas.draw_idle()


# Callback for sliders
def update(val):
    new_heaps = [int(slider.val) for slider in sliders]
    plot_nim(new_heaps)

# Initialize plot
plot_nim(heaps)

# Create sliders
sliders = []
for i in range(len(heaps)):
    ax_slider = plt.axes([0.2, 0.02 + (len(heaps) - i - 1) * 0.07, 0.6, 0.03])
    slider = Slider(ax_slider, f"Heap {i+1}", 0, 10, valinit=heaps[i], valstep=1)
    slider.on_changed(update)
    sliders.append(slider)

plt.show(block=True)