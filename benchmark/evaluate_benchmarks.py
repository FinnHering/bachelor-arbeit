import math
from pathlib import Path
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt




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

    pfs = pfs.groupby("name").agg({"elapsed": "mean", "operations": "mean", "total_elapsed": "mean", "bytes": "mean"}).reset_index()

    return pfs


def plot_barchart(performance: pd.DataFrame, name: str):
    import matplotlib.pyplot as plt

    # plot each metric in a separate plot
    fig, axs = plt.subplots(figsize=(100, 20))

    p = Path(f"benchmark/vis/{name}")
    p.mkdir(parents=True, exist_ok=True)

    performance.plot(kind="barh", x="name", y="elapsed", title="Elapsed Time", figsize=(20, 35), xlim=(0, 7.5))
    plt.savefig(p / "elapsed.png")

    performance.plot(kind="barh", x="name", y="operations", title="Operations", figsize=(30, 20))
    plt.savefig(p / "operations.png")

    performance.plot(kind="barh", x="name", y="total_elapsed", title="Total Elapsed Time", figsize=(30, 20))
    plt.savefig(p / "total_elapsed.png")

    performance.plot(kind="barh", x="name", y="bytes", title="Bytes", figsize=(30, 20))
    plt.savefig(p / "bytes.png")


def plot_benchmarks():
    # get all subfolders except vis
    dirs = [d for d in Path("benchmark").iterdir() if d.is_dir() and d.name != "vis"]

    for dir in dirs:
        
        # skip empty directories
        if not list(dir.iterdir()):
            continue

        res = create_performance_result(dir)
        plot_barchart(res, dir.name)

def compare_benchmarks():
    # get all subfolders except vis
    dirs = [d for d in Path("benchmark").iterdir() if d.is_dir() and d.name != "vis"]

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
    metrics = ["elapsed", "total_elapsed"]
    for metric in metrics:
        res[f"difference_{metric}"] = res[f"{metric}_x"] - res[f"{metric}_y"] 

    print(res[["name", "total_elapsed_x", "total_elapsed_y", "difference_total_elapsed"]])

    # Plot the differences
    p = Path("benchmark/vis/differences")
    p.mkdir(parents=True, exist_ok=True)


    for metric in metrics:
        # use seaborn to plot
        plt.subplots_adjust(left=0.5)
        sns.set_theme(style="whitegrid")
        fig, ax = plt.subplots(figsize=(30, 40))

        sns.barplot(data=res, x=f"difference_{metric}", y="name", orient="h" ) 
        plt.tight_layout()
        plt.savefig(p / f"difference_{metric}.png")




# Call the function to generate the plots
plot_benchmark_differences()

plot_benchmarks()


