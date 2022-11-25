#!/bin/bash

# ------------------------------------------------

# Shell
#PBS -S /bin/bash

# Account
#PBS -A Nastran

# Project
#PBS -P Nastran

# Standard error and standard output are merged
#PBS -j oe
#PBS -koed

# ------------------------------------------------
# --------- MODIFICAR A PARTIR DE AQUI -----------
# Las partes que se deben editar están entre los 
# signos < y >. Estos signos deben ser eliminados
# ------------------------------------------------

# Name
#PBS -N nastran

# Queue
#PBS -q workq

# Runtime (hh:mm:ss)
#PBS -l walltime=9999:00:00

# Mem a cpus
#PBS -l select=1:mpiprocs=1:ncpus=1:mem=4000mb

# ------------------------------------------------

# Change to submission directory

cd $PBS_O_WORKDIR

# Environment configuration

module load nastran/2019

echo """
[ s.hostname = $(hostname) ]
sdir=$TMPDIR
dbs=$TMPDIR/dbs
""" > .nast20191rc_${PBS_JOBID%.*}

mkdir -p $TMPDIR/dbs

# Execution job
baseName=${BDF%%.*}

time nast20191 jid=$BDF append=yes news=no batch=no rcf=.nast20191rc_${PBS_JOBID%.*} memory=4000MB buffsize=65537 scratch=no parallel=$NCPUS

rm -f .nast20191rc_${PBS_JOBID%.*}
