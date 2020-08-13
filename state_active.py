import sys
import pandas as pd

fn = sys.argv[1]
dfi = pd.read_csv(fn, index_col=0, sep=",")
dfi['active'] = dfi.confirmed.cumsum() - dfi.recovered.cumsum() - dfi.deceased.cumsum()
#initial days data can cause negative - make it zero
dfi['active'][dfi['active']<0]  = 0
dfi.to_csv(fn)
