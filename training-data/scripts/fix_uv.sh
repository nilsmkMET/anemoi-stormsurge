#$ -N fix_uv
#$ -l h_rt=3:00:00
#$ -l h_rss=10G,mem_free=10G,h_data=10G
##$ -q bigmem-r8.q
#$ -q research-r8.q
#$ -j y
#$ -o /home/nilsmk/logs/
#$ -e /home/nilsmk/logs/

. /modules/rhel8/conda/install/etc/profile.d/conda.sh
conda activate production-10-2022
cd /home/nilsmk/python
echo $@
y=$@
python merge_era_nora_wind.py $y