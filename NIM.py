import matplotlib.pyplot as plt
from matplotlib.widgets import Slider

# Constants
SAFE_COLOR = "seagreen"
UNSAFE_COLOR = "tomato"
DEFAULT_COLOR = "royalblue"

INITIAL_HEAPS = [1, 3, 5, 7]
MAX_HEAP_SIZE = max(INITIAL_HEAPS)

FIG_SIZE_HEAP = (8, 8)
FIG_SIZE_TABLE = (8, 6)
BOTTOM_ADJUST = 0.1
HEAP_SPACING = 2
CIRCLE_RADIUS = 0.4
NIM_SUM_MIN_BITS = 4

SLIDER_WIDTH = 0.6
SLIDER_HEIGHT = 0.03
SLIDER_START_X = 0.2
SLIDER_START_Y = 0.08
SLIDER_SPACING = 0.05

TABLE_BBOX = [0, 0.5, 1, 0.5]
TABLE_FONT_SIZE = 10
COLUMN_WIDTHS = [0.1, 0.1, 0.15, 0.05, 0.15, 0.05, 0.15, 0.1, 0.15]


class NimGame:
    def __init__(self, heaps):
        self.heaps = list(heaps)
        self.state = self.compute_state()

        self.fig, self.ax = plt.subplots(figsize=FIG_SIZE_HEAP)
        self.fig_info, self.ax_info = plt.subplots(figsize=FIG_SIZE_TABLE)
        self.fig.canvas.manager.set_window_title("🔵 Heap Visualization 🔵")
        self.fig_info.canvas.manager.set_window_title("🧮 Mathematical Insights 🧮")
        self.sliders = []

        self.setup_ui()

    def compute_state(self):
        max_bits = max(NIM_SUM_MIN_BITS, max(self.heaps, default=0).bit_length())
        binary_heaps = [format(heap, f"0{max_bits}b") for heap in self.heaps]
        nim_value = 0
        for heap in self.heaps:
            nim_value ^= heap

        binary_nim_value = format(nim_value, f"0{max_bits}b")
        xor_equation = " ⊕ ".join(binary_heaps) + f" = {binary_nim_value}"

        return {
            "binary_heaps": binary_heaps,
            "nim_value": nim_value,
            "binary_nim_value": binary_nim_value,
            "xor_equation": xor_equation,
        }

    def setup_ui(self):
        plt.subplots_adjust(bottom=BOTTOM_ADJUST)
        self.ax_info.axis("off")
        self.plot_nim()
        self.create_sliders()

    def setup_axes(self):
        self.ax.clear()
        self.ax.set_xlim(-1, len(self.heaps) * HEAP_SPACING)
        self.ax.set_ylim(-0.5, MAX_HEAP_SIZE)
        self.ax.set_xticks(range(0, len(self.heaps) * HEAP_SPACING, HEAP_SPACING))
        self.ax.set_xticklabels([f"Heap {i + 1}" for i in range(len(self.heaps))])
        self.ax.set_yticks([])
        self.ax.set_facecolor("#F5F5F5")
        self.ax.set_aspect("auto")

    def generate_table_data(self):
        binary_width = len(self.state["binary_nim_value"])
        table_data = []

        for index, heap in enumerate(self.heaps):
            moved_value = heap ^ self.state["nim_value"]
            table_data.append(
                [
                    f"Heap {index + 1}",
                    heap,
                    self.state["binary_heaps"][index],
                    "⊕",
                    self.state["binary_nim_value"],
                    "=",
                    format(moved_value, f"0{binary_width}b"),
                    moved_value,
                    "YES" if moved_value < heap else "NO",
                ]
            )

        table_data.append(
            ["Nim-Sum *", self.state["nim_value"], self.state["binary_nim_value"], "", "", "", "", "", ""]
        )
        return table_data

    def draw_heap_circles(self):
        for index, heap in enumerate(self.heaps):
            for level in range(heap):
                self.ax.add_patch(plt.Circle((index * HEAP_SPACING, level), CIRCLE_RADIUS, color=DEFAULT_COLOR))

    def update_table(self):
        self.ax_info.clear()
        self.ax_info.axis("off")

        table_data = self.generate_table_data()
        column_labels = ["Heap#", "Dec", "Bin", "", "Nim-Sum", "", "Bin'", "Dec'", "Safe Move?"]

        table = self.ax_info.table(
            cellText=table_data,
            colLabels=column_labels,
            cellLoc="center",
            loc="center",
            bbox=TABLE_BBOX,
        )
        table.auto_set_font_size(False)
        table.set_fontsize(TABLE_FONT_SIZE)

        for column_index, width in enumerate(COLUMN_WIDTHS):
            table.auto_set_column_width(column_index)
            table.get_celld()[(0, column_index)].set_width(width)

        for (row, _), cell in table.get_celld().items():
            if row == 0:
                cell.get_text().set_weight("bold")

        for row in range(1, len(table_data)):
            safe_move = table_data[row - 1][8] == "YES"
            table.get_celld()[(row, 8)].set_facecolor(SAFE_COLOR if safe_move else UNSAFE_COLOR)

            dec_cell = table.get_celld()[(row, 7)]
            dec_cell.get_text().set_weight("bold")
            dec_cell.get_text().set_color(SAFE_COLOR if safe_move else UNSAFE_COLOR)

        for column_index in range(len(column_labels)):
            cell = table.get_celld()[(len(table_data), column_index)]
            cell.get_text().set_weight("bold")

        self.ax_info.text(
            0.5,
            0.44,
            f"*Nim-Sum = Bitwise XOR of All Heap Sizes: {self.state['xor_equation']}",
            fontsize=10,
            ha="center",
            family="monospace",
        )
        self.ax_info.text(
            0.5,
            0.35,
            "Note: ⊕ represents the bitwise XOR operation, which compares binary digits \n"
            "and returns 1 if they are different and 0 if they are the same.",
            fontsize=9,
            ha="center",
            family="monospace",
        )

    def plot_nim(self):
        self.state = self.compute_state()
        self.setup_axes()
        self.ax.set_title(
            f"Nim-Sum = {self.state['nim_value']} ({self.state['binary_nim_value']}) "
            f"({'Safe' if self.state['nim_value'] == 0 else 'Unsafe'})",
            fontsize=14,
            color=SAFE_COLOR if self.state["nim_value"] == 0 else UNSAFE_COLOR,
        )

        self.draw_heap_circles()
        self.update_table()
        self.fig.canvas.draw_idle()
        self.fig_info.canvas.draw_idle()

    def create_sliders(self):
        for index, heap in enumerate(self.heaps):
            axes = plt.axes([SLIDER_START_X, SLIDER_START_Y + (len(self.heaps) - index - 1) * SLIDER_SPACING, SLIDER_WIDTH, SLIDER_HEIGHT])
            slider = Slider(axes, f"Heap {index + 1}", 0, MAX_HEAP_SIZE, valinit=heap, valstep=1)
            slider.on_changed(self.update)
            self.sliders.append(slider)

    def update(self, _):
        self.heaps = [int(slider.val) for slider in self.sliders]
        self.plot_nim()


if __name__ == "__main__":
    nim_game = NimGame(INITIAL_HEAPS)
    plt.show(block=True)
