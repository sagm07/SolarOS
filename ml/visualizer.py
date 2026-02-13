import numpy as np

def generate_ascii_plot(data, title="Efficiency Trend", height=10, width=50):
    """
    Generates a simple ASCII line plot for the terminal.
    
    Args:
        data (list/array): Series of values to plot.
        title (str): Plot title.
        height (int): Height of the plot in lines.
        width (int): Width of the plot in characters.
    """
    if data is None or len(data) == 0:
        return "No data to plot."
        
    y = np.array(data)
    y_min, y_max = y.min(), y.max()
    y_range = y_max - y_min
    
    if y_range == 0:
        y_range = 1
        
    # Scale x to fit width
    x_indices = np.linspace(0, len(y) - 1, width).astype(int)
    y_scaled = y[x_indices]
    
    # Create canvas
    canvas = [[' ' for _ in range(width)] for _ in range(height)]
    
    # Plot points
    for x_idx, value in enumerate(y_scaled):
        # Normalized height 0 to 1
        norm_h = (value - y_min) / y_range
        # Scale to row index (height-1 is 0, 0 is max)
        row_idx = int((1.0 - norm_h) * (height - 1))
        canvas[row_idx][x_idx] = '*'
        
    # Build string
    output = []
    output.append(f"--- {title} ---")
    output.append(f"{y_max:.2f} | " + "".join(canvas[0]))
    
    for row in canvas[1:-1]:
        output.append("       | " + "".join(row))
        
    output.append(f"{y_min:.2f} | " + "".join(canvas[-1]))
    output.append("       " + "-" * width)
    
    return "\n".join(output)

def plot_dust_vs_efficiency(dust_levels, efficiencies):
    """
    Plots two lines: Dust (increasing) and Efficiency (decreasing).
    For simplicity in ASCII, we'll just plot Efficiency since it's the KPI.
    """
    return generate_ascii_plot(efficiencies, title="Solar Efficiency Trend (Degradation)")

if __name__ == "__main__":
    # Test
    t = np.linspace(0, 10, 100)
    eff = 20.0 * (1.0 - 0.02 * t) # Linear decay
    print(plot_dust_vs_efficiency(None, eff))
