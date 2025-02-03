import math
from pathlib import Path
from matplotlib.ticker import MultipleLocator
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

benchmark_folder_names = {"system", "apptainer"}



def parse_file(file: Path) -> pd.DataFrame:
    with open(file, "r") as f:
        lines = f.readlines()

    
    
    header = lines[0].strip().split("\t")

    print(header)

    performance = pd.DataFrame(columns=header)
    print("done")

    for line in lines[1:]:
        values = line.strip().split("\t")
        print(values)
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


def plot_barchart(performance: pd.DataFrame, name: str):
    import matplotlib.pyplot as plt

    # plot each metric in a separate plot
    fig, axs = plt.subplots(figsize=(30, 20))

    p = Path(f"benchmark/vis/{name}")
    p.mkdir(parents=True, exist_ok=True)

    performance.plot(kind="barh", x="name", y="operations", title="Operations", logx=True, ax=axs)
    fig.tight_layout()
    
    plt.savefig(p / "operations.png")


def plot_benchmarks():
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


def plot_benchmark_differences():

    # Load the benchmark results
    res = compare_benchmarks()

    # Get the system benchmark
    system = res[res["dir"] == "system"]

    # Remove the system benchmark from the results
    res = res[res["dir"] != "system"]

    print(res)


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
        sns.set_theme(style="whitegrid")
        fig, ax = plt.subplots(figsize=(30, 40))

        ax = sns.barplot(data=res, x=f"difference_{metric}", y="name", orient="h") 
        ax.xaxis.set_ticks_position('bottom')
        ax.tick_params(which='major', width=1.00)
        ax.tick_params(which='major', length=5)
        ax.tick_params(which='minor', width=0.75)
        ax.tick_params(which='minor', length=2.5)
        ax.xaxis.set_major_locator(MultipleLocator(1))
        ax.xaxis.set_minor_locator(MultipleLocator(0.1))
        plt.tight_layout()
        plt.savefig(p / f"difference_{metric}.png")


def plot_subname_differences():
    res = compare_benchmarks()
    # Only capture the highest category before the first slash
    subnames = res['name'].str.extract(r'^([^/]+)/')[0].dropna().unique()

    for sub in subnames:
        # Filter by names that start with the highest category
        subres = res[res['name'].str.startswith(f"{sub}/")]
        if subres.empty:
            continue

        system = subres[subres["dir"] == "system"]
        subres = subres[subres["dir"] != "system"]
        if system.empty or subres.empty:
            continue

        subres = pd.merge(subres, system, on="name")
        metrics = ["operations", "total_elapsed"]

        for metric in metrics:
            subres[f"difference_{metric}"] = subres[f"{metric}_x"] / subres[f"{metric}_y"]

        sub_dir_name = sub.strip("/")
        p = Path(f"benchmark/vis/differences/{sub_dir_name}")
        p.mkdir(parents=True, exist_ok=True)

        for metric in metrics:
            plt.subplots_adjust(left=0.5)
            sns.set_theme(style="whitegrid")
            fig, ax = plt.subplots(figsize=(30, 40))

            ax = sns.barplot(data=subres, x=f"difference_{metric}", y="name", orient="h")
            ax.xaxis.set_ticks_position('bottom')
            ax.tick_params(which='major', width=1.00)
            ax.tick_params(which='major', length=5)
            ax.tick_params(which='minor', width=0.75)
            ax.tick_params(which='minor', length=2.5)
            ax.xaxis.set_major_locator(MultipleLocator(1))
            ax.xaxis.set_minor_locator(MultipleLocator(0.1))
            plt.tight_layout()
            plt.savefig(p / f"difference_{metric}.png")


def export_boxplot(dir: Path):
    performances = parse_all_files(Path(dir))
    pfs = pd.concat(performances, ignore_index=True).reset_index()


    plt.figure(figsize=(20, 30))
    sns.set_theme(style="whitegrid")
    ax = sns.boxplot(data=pfs, y="name", x="total_elapsed")
    ax.xaxis.set_major_locator(MultipleLocator(0.5))
    ax.title.set_text(f"Total Elapsed Time ({dir.name})")

    plt.savefig(f"benchmark/vis/{dir.name}_boxplot.svg")

def export_boxplots():
    dirs = [d for d in Path("benchmark").iterdir() if d.is_dir() and d.name in benchmark_folder_names]

    for dir in dirs:
        export_boxplot(dir)




if __name__ == "__main__":

    sns.set_theme(rc={"xtick.bottom" : True, "ytick.left" : True})
    # Call the function to generate the plots
    plot_benchmark_differences()
    plot_subname_differences()
    plot_benchmarks()
    #export_boxplots()


