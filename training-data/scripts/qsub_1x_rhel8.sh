#$ -N qsub1x
#$ -l h_rt=10:00:00
##$ -l h_rss=350G,mem_free=350G,h_data=350G
##$ -l h_rss=200G,mem_free=200G,h_data=200G
##$ -l h_rss=50G,mem_free=50G,h_data=50G
#$ -l h_rss=10G,mem_free=10G,h_data=10G
##$ -q bigmem-r8.q
#$ -q research-r8.q
#$ -j y
#$ -o /home/nilsmk/logs/
#$ -e /home/nilsmk/logs/

. /modules/rhel8/conda/install/etc/profile.d/conda.sh
conda activate production-10-2022
echo $@
$@
