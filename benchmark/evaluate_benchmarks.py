import math
from pathlib import Path
from matplotlib.ticker import MultipleLocator
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

benchmark_folder_names = {"system", "apptainer"}


def compress_benchmark(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove rows whose 'name' contains 'batch' (or other similar results).
    """
    df = df[~df["name"].str.contains("batch", case=False, na=False)]
    df = df[~df["name"].str.contains("index-single", case=False, na=False)]
    df = df[~df["name"].str.contains("index-mixed", case=False, na=False)]
    df = df[~df["name"].str.contains("index-all", case=False, na=False)]

    return df   


def parse_file(file: Path) -> pd.DataFrame:
    with open(file, "r") as f:
        lines = f.readlines()

    
    header = lines[0].strip().split("\t")
    performance = pd.DataFrame(columns=header)

    for line in lines[1:]:
        values = line.strip().split("\t")
        performance = pd.concat([performance, pd.DataFrame([values], columns=header)], ignore_index=True)

    performance = performance.infer_objects()

    performance["bytes"] = performance["bytes"].replace("-", None)

    return performance.astype({"name": "string", "elapsed": "float64", "operations": "float64", "bytes": "float64", "total_elapsed": "float64"})


def parse_all_files(dir: Path) -> list[pd.DataFrame]:
    return [parse_file(file) for file in dir.iterdir() if file.is_file() and file.suffix == ".out"]


def create_performance_result(dir: Path) -> pd.DataFrame:
    performances = parse_all_files(dir)
   
    pfs = pd.concat(performances, ignore_index=True).reset_index()

    # group by name and mean of elapsed, operations, total_elapsed

    pfs = pfs.groupby("name").agg({"elapsed": "median", "operations": "median", "total_elapsed": "median", "bytes": "median"}).reset_index()

    return pfs

def create_unaggregated_performance_result(dir: Path) -> pd.DataFrame:
    performances = parse_all_files(dir)

    pfs = pd.concat(performances, ignore_index=True).reset_index()
    return compress_benchmark(pfs)


def plot_barchart(performance: pd.DataFrame, name: str):
    import matplotlib.pyplot as plt

    # plot each metric in a separate plot
    fig, axs = plt.subplots(figsize=(30, 20))

    p = Path(f"benchmark/vis/{name}")
    p.mkdir(parents=True, exist_ok=True)

    performance.plot(kind="barh", x="name", y="operations", title="Operations", logx=True, ax=axs)
    fig.tight_layout()
    
    plt.savefig(p / "operations.svg")


def plot_full_benchmarks():
    # get all subfolders except vis
    dirs = [d for d in Path("benchmark").iterdir() if d.is_dir() and d.name in benchmark_folder_names]

    for dir in dirs:
        
        # skip empty directories
        if not list(dir.iterdir()):
            continue

        res = create_performance_result(dir)
        plot_barchart(res, dir.name)

def compare_benchmarks(base_folder: Path = Path("benchmark")) -> pd.DataFrame:
    # get all subfolders except vis
    dirs = [d for d in base_folder.iterdir() if d.is_dir() and d.name  in benchmark_folder_names]

    res = pd.DataFrame()

    for dir in dirs:
        
        # skip empty directories
        if not list(dir.iterdir()):
            continue

        performance_res = create_performance_result(dir)
        performance_res["dir"] = dir.name

        res = pd.concat([res, performance_res], ignore_index=True)

    return res

def plot_run_to_run_differences():

    # Apptainer results
    performances_apptainer = parse_all_files(Path("benchmark/apptainer"))
    pfs_apptainer = compress_benchmark(pd.concat(performances_apptainer, ignore_index=True).reset_index())

    # System results
    performances_system = parse_all_files(Path("benchmark/system"))
    pfs_system = compress_benchmark(pd.concat(performances_system, ignore_index=True).reset_index())

    pfs_total = pd.merge(pfs_apptainer, pfs_system, on="name")

    pfs_total["difference_operations"] = (pfs_total["operations_x"] / pfs_total["operations_y"]) - 1


    p = Path("benchmark/vis/compressed/differences/")

    p.mkdir(parents=True, exist_ok=True)

    plt.figure(figsize=(30, 10))
    ax = sns.boxplot(data=pfs_total, x="difference_operations", y="name")
    ax.title.set_text(f"Verteilung der Laufzeitunterschiede zwischen Apptainer und System")

    ax.tick_params(which='major', width=0.01)
    ax.tick_params(axis="x", rotation=-90)
    ax.xaxis.set_major_locator(MultipleLocator(0.01))

    ax.set_xlim(-0.5, 0.6)

    plt.tight_layout()
    plt.savefig(p / "run_to_run_distribution.svg")



def plot_compressed_benchmark_differences():

    # Load the benchmark results
    res = compress_benchmark(compare_benchmarks())

    # Get the system benchmark
    system = res[res["dir"] == "system"]

    # Remove the system benchmark from the results
    res = res[res["dir"] == "apptainer"]

    res = pd.merge(res, system, on="name")
    # Calculate the difference in performance
    metrics = ["operations"]


    # create relative differences


    for metric in metrics:
        res[f"difference_{metric}"] = (res[f"{metric}_x"] / res[f"{metric}_y"]) - 1


    # Plot the differences
    p = Path("benchmark/vis/compressed/differences")
    p.mkdir(parents=True, exist_ok=True)


    for metric in metrics:
        # use seaborn to plot
        plt.subplots_adjust(left=0.5)
        
        fig, ax = plt.subplots(figsize=(20, 30))

        ax = sns.barplot(data=res, x=f"difference_{metric}", y="name", orient="h") 
        ax.xaxis.set_ticks_position('bottom')
        ax.tick_params(which='major', width=0.01)
        ax.tick_params(which='minor', width=0.001)
        ax.tick_params(axis="x", rotation=-90)
        ax.xaxis.set_major_locator(MultipleLocator(0.01))
        ax.xaxis.set_minor_locator(MultipleLocator(0.001))
        
        # set x boundaries to -0.3, 0.3
        ax.set_xlim(-0.25, 0.25)

        plt.tight_layout()
        plt.savefig(p / f"difference_{metric}.svg")

def plot_full_benchmark_differences():

    # Load the benchmark results
    res = compare_benchmarks()

    # Get the system benchmark
    system = res[res["dir"] == "system"]

    # Remove the system benchmark from the results
    res = res[res["dir"] != "system"]

    res = pd.merge(res, system, on="name")
    # Calculate the difference in performance
    metrics = ["operations", "total_elapsed"]


    # create relative differences


    for metric in metrics:
        res[f"difference_{metric}"] = res[f"{metric}_x"] / res[f"{metric}_y"]


    # Plot the differences
    p = Path("benchmark/vis/differences")
    p.mkdir(parents=True, exist_ok=True)


    for metric in metrics:
        # use seaborn to plot
        plt.subplots_adjust(left=0.5)
        fig, ax = plt.subplots(figsize=(30, 40))


        sns.set_theme(rc={"xtick.bottom" : True, "ytick.left" : True}, font_scale=1)
        ax = sns.barplot(data=res, x=f"difference_{metric}", y="name", orient="h") 
        ax.xaxis.set_ticks_position('bottom')
        ax.tick_params(which='major', width=1.00)
        ax.tick_params(which='major', length=5)
        ax.tick_params(which='minor', width=0.75)
        ax.tick_params(which='minor', length=2.5)
        ax.xaxis.set_major_locator(MultipleLocator(1))
        ax.xaxis.set_minor_locator(MultipleLocator(0.1))
        plt.tight_layout()
        plt.savefig(p / f"difference_{metric}.svg")


def plot_compressed_subname_differences():
    sns.set_theme(rc={"xtick.bottom" : True, "ytick.left" : True}, font_scale=1.5, style="whitegrid")

    res = compress_benchmark(compare_benchmarks())

    # Only capture the highest category before the first slash
    subnames = res['name'].str.extract(r'^/([^/]+)/')[0].dropna().unique()

    for sub in subnames:
        # Filter by names that start with the highest category
        f_vals = res[res['name'].str.startswith(f"/{sub}/")]
        if f_vals.empty:
            print(f"Empty: {sub}")
            continue

        system = f_vals[f_vals["dir"] == "system"]
        apptainer = f_vals[f_vals["dir"] == "apptainer"]
        if system.empty or apptainer.empty:
            continue

        full = pd.merge(apptainer, system, on="name")
        metrics = ["operations", "total_elapsed"]

        for metric in metrics:
            full[f"difference_{metric}"] = (full[f"{metric}_x"] / full[f"{metric}_y"]) - 1

        min_diff = full[f"difference_operations"].min() - 0.005
        max_diff = full[f"difference_operations"].max() + 0.005

        sub_dir_name = sub.strip("/")
        p = Path(f"benchmark/vis/compressed/differences/{sub_dir_name}")
        p.mkdir(parents=True, exist_ok=True)

        for metric in metrics:
            plt.close('all')

            print(f"{sub}: {5.0 * (full.shape[0] / 5.0)}")

            plt.figure(constrained_layout=True, figsize=(20, max(5.0 * (full.shape[0] / 4.0), 2.0)))

            ax = sns.barplot(data=full, x=f"difference_{metric}", y="name", orient="h")
            ax.xaxis.set_ticks_position('bottom')
            ax.tick_params(axis="x", rotation=-90)
            ax.xaxis.set_major_locator(MultipleLocator(0.01))
            ax.xaxis.set_minor_locator(MultipleLocator(0.0025))
            ax.relim(visible_only=True)

            print(f"{sub}: {min_diff} {max_diff}")

            ax.set_xlim(max(-0.25, min(min_diff, 0)), min(0.25, max(max_diff, 0)))
            #plt.tight_layout()
            plt.savefig(p / f"difference_{metric}.svg", bbox_inches='tight')


def plot_full_subname_differences():
    res = compare_benchmarks()
    # Only capture the highest category before the first slash
    subnames = res['name'].str.extract(r'^/([^/]+)/')[0].dropna().unique()

    for sub in subnames:
        # Filter by names that start with the highest category
        apptainer = res[res['name'].str.startswith(f"/{sub}/")]
        if apptainer.empty:
            continue

        system = apptainer[apptainer["dir"] == "system"]
        apptainer = apptainer[apptainer["dir"] == "apptainer"]
        if system.empty or apptainer.empty:
            continue

        full = pd.merge(apptainer, system, on="name")
        metrics = ["operations", "total_elapsed"]

        for metric in metrics:
            full[f"difference_{metric}"] = (full[f"{metric}_x"] / full[f"{metric}_y"]) - 1 

        sub_dir_name = sub.strip("/")
        p = Path(f"benchmark/vis/differences/{sub_dir_name}")
        p.mkdir(parents=True, exist_ok=True)

        for metric in metrics:
            plt.subplots_adjust(left=0.5)
            fig, ax = plt.subplots(figsize=(30, 40))

            ax = sns.barplot(data=full, x=f"difference_{metric}", y="name", orient="h")
            ax.xaxis.set_ticks_position('bottom')
            ax.tick_params(which='major', width=1.00)
            ax.tick_params(which='major', length=5)
            ax.tick_params(which='minor', width=0.75)
            ax.tick_params(which='minor', length=2.5)
            ax.xaxis.set_major_locator(MultipleLocator(1))
            ax.xaxis.set_minor_locator(MultipleLocator(0.1))
            plt.tight_layout()
            plt.savefig(p / f"difference_{metric}.svg")

def plot_compressed_boxplots_raw():
    system_files = parse_all_files(Path("benchmark/system"))
    df_system = compress_benchmark(pd.concat(system_files, ignore_index=True))

    apptainer_files = parse_all_files(Path("benchmark/apptainer"))
    df_apptainer = compress_benchmark(pd.concat(apptainer_files, ignore_index=True))

    p = Path(f"benchmark/vis/compressed/boxplots/system/")
    p.mkdir(parents=True, exist_ok=True)

    plt.figure(figsize=(30, 30))
    ax = sns.boxplot(data=df_system, x="operations", y="name")
    ax.set_xscale("log")
    ax.title.set_text(f"Nativ")
    plt.tight_layout()
    plt.savefig(p / "boxplot.svg")

    p = Path(f"benchmark/vis/compressed/boxplots/apptainer/")
    p.mkdir(parents=True, exist_ok=True)

    plt.figure(figsize=(30, 30))
    ax = sns.boxplot(data=df_apptainer, x="operations", y="name")
    ax.set_xscale("log")
    ax.title.set_text(f"Apptainer")
    plt.tight_layout()
    plt.savefig(p / "boxplot.svg")

def plot_compressed_subname_boxplots_raw():
    system_files = parse_all_files(Path("benchmark/system"))
    df_system = compress_benchmark(pd.concat(system_files, ignore_index=True))

    apptainer_files = parse_all_files(Path("benchmark/apptainer"))
    df_apptainer = compress_benchmark(pd.concat(apptainer_files, ignore_index=True))

    # Process system data
    subnames_system = df_system['name'].str.extract(r'^/([^/]+)/')[0].dropna().unique()

    for sub in subnames_system:
        sub_data_sys = df_system[df_system['name'].str.startswith(f"/{sub}/")]
        if sub_data_sys.empty:
            continue

        p = Path(f"benchmark/vis/compressed/boxplots/system/{sub.strip('/')}")
        p.mkdir(parents=True, exist_ok=True)

        plt.figure(figsize=(30, 10))
        ax = sns.boxplot(data=sub_data_sys, x="operations", y="name")
        ax.title.set_text(f"System - {sub.strip('/')}")
        plt.tight_layout()
        plt.savefig(p / "boxplot.svg")

    # Process apptainer data
    subnames_appt = df_apptainer['name'].str.extract(r'^/([^/]+)/')[0].dropna().unique()
    for sub in subnames_appt:
        sub_data_app = df_apptainer[df_apptainer['name'].str.startswith(f"/{sub}/")]
        if sub_data_app.empty:
            continue

        p = Path(f"benchmark/vis/compressed/boxplots/apptainer/{sub.strip('/')}")
        p.mkdir(parents=True, exist_ok=True)

        plt.figure(figsize=(30, 10))
        
        should_log = sub == "message"

        ax = sns.boxplot(data=sub_data_app, x="operations", y="name")
        ax.title.set_text(f"Apptainer - {sub.strip('/')}")
        if should_log:
            ax.set_xscale("log")
        plt.tight_layout()
        plt.savefig(p / "boxplot.svg")


def draw_broken_boxplot(data: pd.DataFrame, x: str, y: str, title: str, path: Path, *breakpoints: tuple[int, int]):

    new_data = data.iloc[0:0] 

    for breakpoint in sorted(breakpoints, key=lambda x: x[0], reverse=True):
        new_data = new_data.append(data.where(~data[x].between(*breakpoint), None))

    
    num_breakpoints = len(breakpoints)

    fig, axs = plt.subplots(num_breakpoints + 1, 1, figsize=(30, 10 * (num_breakpoints + 1)))

    for i, ax in enumerate(axs):
        sns.boxplot(data=new_data, x=x, y=y, ax=ax)

def plot_full_subname_boxplots_raw():
    system_files = parse_all_files(Path("benchmark/system"))
    df_system = pd.concat(system_files, ignore_index=True)

    apptainer_files = parse_all_files(Path("benchmark/apptainer"))
    df_apptainer = pd.concat(apptainer_files, ignore_index=True)

    # Process system data
    subnames_system = df_system['name'].str.extract(r'^/([^/]+)/')[0].dropna().unique()

    for sub in subnames_system:
        sub_data_sys = df_system[df_system['name'].str.startswith(f"/{sub}/")]
        if sub_data_sys.empty:
            continue

        p = Path(f"benchmark/vis/boxplots/system/{sub.strip('/')}")
        p.mkdir(parents=True, exist_ok=True)

        plt.figure(figsize=(20, 10))
        
        ax = sns.boxplot(data=sub_data_sys, x="operations", y="name")
        ax.title.set_text(f"System - {sub.strip('/')}")
        plt.tight_layout()
        plt.savefig(p / "boxplot.svg")

    # Process apptainer data
    subnames_appt = df_apptainer['name'].str.extract(r'^/([^/]+)/')[0].dropna().unique()
    for sub in subnames_appt:
        sub_data_app = df_apptainer[df_apptainer['name'].str.startswith(f"/{sub}/")]
        if sub_data_app.empty:
            continue

        p = Path(f"benchmark/vis/boxplots/apptainer/{sub.strip('/')}")
        p.mkdir(parents=True, exist_ok=True)

        plt.figure()
        
        ax = sns.boxplot(data=sub_data_app, x="operations", y="name")
        ax.title.set_text(f"Apptainer - {sub.strip('/')}")
        plt.tight_layout()
        plt.savefig(p / "boxplot.svg")

def plot_compare_disribution_hist(metric: str, bins: int = 15):

    sns.set_theme(rc={"xtick.bottom" : True, "ytick.left" : True}, font_scale=2.5, style="whitegrid")

    apptainer_data = create_unaggregated_performance_result(Path("benchmark/apptainer"))
    apptainer_data = apptainer_data.assign(dir='apptainer')
    system_data = create_unaggregated_performance_result(Path("benchmark/system"))
    system_data = system_data.assign(dir='system')
    
    full_data = pd.concat([apptainer_data, system_data], ignore_index=True)
    full_data = full_data[full_data["name"] == metric]

    if full_data.empty:
        print(f"Metric {metric} not found")
        return
    

    p = Path(f"benchmark/vis/compressed/differences/comparisons/")
    p.mkdir(parents=True, exist_ok=True)

    plt.figure(figsize=(20, 10))
    ax = sns.histplot(data=full_data, x="operations", hue="dir", multiple="stack", bins=bins)
    ax.title.set_text(f"Verteilung der Laufzeitunterschiede zwischen Apptainer und System")

    #sanitize metric 
    metric = metric.replace("/", "_")

    plt.tight_layout()
    plt.savefig(p / f"run_to_run_distribution_{metric}.svg")

if __name__ == "__main__":


    sns.set_theme(rc={"xtick.bottom" : True, "ytick.left" : True}, font_scale=2.5, style="whitegrid")
    ax = plt.gca()
    ax.tick_params(width=5)
    # Call the function to generate the plots
    plot_full_benchmark_differences()
    plt.close('all')

    plot_full_subname_differences()
    plt.close('all')

    plot_full_benchmarks()
    plt.close('all')

    plot_full_subname_boxplots_raw()
    plt.close('all')

    plot_compressed_subname_differences()
    plt.close('all')

    plot_compressed_subname_boxplots_raw()
    plt.close('all')

    plot_compressed_benchmark_differences()
    plt.close('all')

    plot_compressed_boxplots_raw()
    plt.close('all')

    plot_run_to_run_differences()
    plt.close('all')

    plot_compare_disribution_hist("/item/collection/create")
    plt.close('all')

    plot_compare_disribution_hist("/db/entry/update", bins=30)
    plt.close('all')

    plot_compare_disribution_hist("/db/schema/create", bins=10)
    plt.close('all')

    plot_compare_disribution_hist("/db/schema/delete", bins=10)
    plt.close('all')

    #export_boxplots()


