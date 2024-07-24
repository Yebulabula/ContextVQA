

import os

# move the first 10 folders from the root to the ContextVQA folder
for folder in os.listdir('../Backup/3D_scans')[:10]:
    os.system(f'mv ../Backup/3D_scans/{folder} 3D_scans/{folder}')