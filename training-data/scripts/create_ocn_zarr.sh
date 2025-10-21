#$ -N create_ocn
#$ -l h_rt=3:00:00
#$ -l h_rss=10G,mem_free=10G,h_data=10G
##$ -q bigmem-r8.q
#$ -q research-r8.q
#$ -j y
#$ -o /home/nilsmk/logs/
#$ -e /home/nilsmk/logs/

# set -x
. /modules/rhel8/conda/install/etc/profile.d/conda.sh
conda deactivate
source /home/nilsmk/venv/anemoi/bin/activate
cd /home/nilsmk/GIT/anemoi-stormsurge/training-data/config/single_years
echo $@
y=$@
anemoi-datasets create nordic4_surge_ocean_${y}.yaml /lustre/storeB/users/nilsmk/anemoi-datasets/input/nordic4_surge_ocean_corrected_${y}.zarr --overwrite
# set +x