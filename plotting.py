def plot_subname_differences(data, *args, **kwargs):
    """
    Create a plot for each subname.

    Parameters:
    - data: The data to plot.
    - *args, **kwargs: Additional arguments passed to plot_benchmark_differences.
    """
    subnames = data['name'].str.extract(r'^([^/]+)/')[0].dropna().unique()
    for subname in subnames:
        subname_data = data[data['name'].str.startswith(f"{subname}/")]
        plot_benchmark_differences(subname_data, *args, **kwargs)

# ...existing code...
