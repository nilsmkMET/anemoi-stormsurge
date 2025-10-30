#$ -N merge_ocn
#$ -l h_rt=48:00:00
#$ -l h_rss=30G,mem_free=30G,h_data=30G
##$ -q bigmem-r8.q
#$ -q research-r8.q
##$ -pe shmem-8 8
#$ -j y
#$ -o /home/nilsmk/logs/
#$ -e /home/nilsmk/logs/

# set -x
. /modules/rhel8/conda/install/etc/profile.d/conda.sh
conda deactivate
source /home/nilsmk/venv/anemoi/bin/activate
cd /home/nilsmk/GIT/anemoi-stormsurge/training-data/config/
anemoi-datasets create nordic4_surge_ocean_corrected_1990-2018.yaml /lustre/storeB/users/nilsmk/anemoi-datasets/input/nordic4_surge_ocean_corrected_1990-2018.zarr --overwrite --processes 8
# set +x