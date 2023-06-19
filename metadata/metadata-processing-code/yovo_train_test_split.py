import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from numpy.random import RandomState

df = pd.read_csv('/Volumes/RR/yovo_asr/line_index_asr.tsv', sep="\t", header=None)

train = df.sample(frac=0.75, random_state=RandomState())        # 0.75
not_train = df.loc[~df.index.isin(train.index)]                 # 0.25

dev = not_train.sample(frac=0.2, random_state=RandomState())    # 0.2 * 0.25 == 0.05
test = not_train.loc[~not_train.index.isin(dev.index)]          # the remaining which is 0.20

# sort
sorted_train = train.sort_values(0)
sorted_dev = dev.sort_values(0)
sorted_test = test.sort_values(0)

# write new files
sorted_train.to_csv('line_index_asr_train.tsv', index=False, sep="\t", header=False)
sorted_dev.to_csv('line_index_asr_dev.tsv', index=False, sep="\t", header=False)
sorted_test.to_csv('line_index_asr_test.tsv', index=False, sep="\t", header=False)