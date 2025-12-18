#!/bin/bash
# Run the LinkedIn Login app

cd "$(dirname "$0")"

# Activate conda environment
source /Applications/anaconda3/etc/profile.d/conda.sh
conda activate invoice-getter

# Run streamlit
streamlit run app.py --server.port 3940

