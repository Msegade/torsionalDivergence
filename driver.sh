#!/bin/bash

# $1 and $2 are special variables in bash that contain the 1st and 2nd 
# command line arguments to the script, which are the names of the
# Dakota parameters and results files, respectively.

params=$1
results=$2

############################################################################### 
##
## Pre-processing Phase -- Generate/configure an input file for your simulation 
##  by substiting in parameter values from the Dakota paramters file.
##
###############################################################################

cp ../parameters.yaml.template .
ln -fs ../dodo.py dodo.py
ln -fs ../coefficients_filtered.mat coefficients_filtered.mat
ln -fs ../config.py config.py
ln -fs ../complete_t.py complete_t.py
ln -fs ../loads_t.m loads_t.m
ln -fs ../main.bdf main.bdf
ln -fs ../MDA.py MDA.py
ln -fs ../modelBDF.h5 modelBDF.h5
ln -fs ../model-modal-nLinear-restart.bdf model-modal-nLinear-restart.bdf
ln -fs ../post.py post.py
ln -fs ../processModes.py processModes.py
ln -fs ../Wing.py Wing.py
dprepro $params parameters.yaml.template parameters.yaml

############################################################################### 
##
## Execution Phase -- Run your simulation
##
###############################################################################
# Cluster
################################
#sshC="ssh -l mrodriguez -t breogan.udc.es"
#doit optModel
#dirname=$(basename $(pwd))
#parentDir=/home/mrodriguez/ESA/model2
#remoteDir=$parentDir/$dirname
#$sshC "mkdir $remoteDir"
#scp optModel.bdf mrodriguez@breogan.udc.es:$remoteDir/.
#scp post.py mrodriguez@breogan.udc.es:$remoteDir/.
#$sshC "ln -sf $parentDir/nastran20191.sh $remoteDir/."
#$sshC "cd $remoteDir &&  qsub -Wblock=true nastran20191.sh"
#scp mrodriguez@breogan.udc.es:$remoteDir/resultsFinal.json .
#rm *.bdf
#rm groups.pkl
#rm classes.pkl
#rm counters.pkl

# Local
################################
if [[ "$(hostname)" == *'ve'* ]]; then
    PYTHON=python
elif [[ "$(hostname)" == *'breogan'* ]]; then
    PYTHON=pythonLaunch
fi
$PYTHON MDA.py nLinear
#doit design
#sed "s/#NAME/#PBS -N $(basename $PWD)/" doit-template.sh > doit-launcher.sh
#qsub -Wblock=true doit-launcher.sh
##singularity exec /home/mrodriguez/Documentos/Tesis/singularity/arch/arch.sif doit design

############################################################################### 
##
## Post-processing Phase -- Extract (or calculate) quantities of interest
##  from your simulation's output and write them to a properly-formatted
##  Dakota results file.
##
###############################################################################

mode=$(jq '.mode' results.json)

echo $mode > $results

#jpr10=$(jq '.jpr10' results.json)

#derivNumber=$(grep obj_fn $params | awk '{print $1}')
# Convert to an array
#readarray -t darray < <(echo $derivNumber)
# Convert to an array
#readarray -t darray < <(grep obj_fn $params | awk '{print $1}')

#echo "Deriv number 1 = $derivNumber" | cat -A 
#echo "Deriv number 1 = ${darray[0]}" | cat -A 


#if $(test "$derivNumber" -eq 1); then
#    echo "$vArea vArea" > $results
#fi

#if [[ "${darray[0]}" == 1 ]]; then
#    echo "$vArea vArea" > $results
#    echo "$mass mass" >> $results
#elif [[ "${darray[1]}" == 2 ]]; then
#    echo "[ $jpr1 $jpr2 $jpr3 $jpr4 $jpr5 $jpr6 $jpr7 $jpr8 $jpr9 $jpr10 ]" > $results
#fi

