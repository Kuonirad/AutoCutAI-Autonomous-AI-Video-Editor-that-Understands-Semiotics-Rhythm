# Step 4: Causal DAG in one Python call

# 4.1  Build a tidy data-frame: col_0 = error flag, cols 1..k = basic-block hit counts
#      (already emitted by clang -fprofile-arcs)
import pandas as pd
import tigramite.data_processing as pp
import numpy as np
from tigramite.pcmci import PCMCI
from tigramite.independence_tests import GPDC

# This script assumes 'bb_counts.csv' is present.
# In a real scenario, a prior step would generate this file.
# For now, we assume it has column names corresponding to basic blocks
# and the first column is an error flag.
df = pd.read_csv('bb_counts.csv')
dataframe = pp.DataFrame(df.values, var_names=df.columns)

# 4.2  Run PCMCI+ (alpha=0.01, maxlag=5)
pcmci = PCMCI(dataframe=dataframe, cond_ind_test=GPDC())
results = pcmci.run_pcmciplus(tau_max=5, pc_alpha=0.01)
dag = results['graph']                     # numpy array

# 4.3  Root-cause = parents of the error node (column 0, the error flag)
# NOTE: The logic for finding root causes has been a source of confusion.
# The implementation below is a best-effort attempt based on the user's
# original code and subsequent feedback, but may still be incorrect.
# It looks for parents of node 0 at lag 0.
root_causes = np.where(dag[:, 0, 0] == '-->')[0]
print(f"ROOT_CAUSES={','.join(map(str, root_causes))}")
