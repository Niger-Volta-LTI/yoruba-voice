import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def plot_corpus_partition(partition_csv):
    column_names = ["Uttid", "Loudness", "Duration"]
    df = pd.read_csv(partition_csv, sep='\t', names=column_names)
    print(df.head(5))

    plt.figure(figsize=(20, 20))
    sns.set_style('darkgrid')

    # plot Duration Data
    h = sns.histplot(data=df, x="Duration", bins=40)
    h.set_xlabel("Duration (in seconds)", fontsize=40)
    h.set_ylabel("Count", fontsize=40)
    h.tick_params(labelsize=40)
    plt.show()

    # plot Loudness data
    plt.figure(figsize=(20, 20))
    h = sns.histplot(data=df, x="Loudness", bins=40)
    h.set_xlabel("Loudness (in LUFS)", fontsize=40)
    h.set_ylabel("Count", fontsize=40)
    h.tick_params(labelsize=40)
    plt.show()


if __name__ == "__main__":
    plot_corpus_partition(partition_csv="./asr_stats.tsv")
    plot_corpus_partition(partition_csv="./tts_stats.tsv")
