from socket import gethostname

if 'breogan' in gethostname():
   # Octave Container
   sing = '/opt/ohpc/pub/libs/singularity/3.4.1/bin/singularity'
   sif = '/home/mrodriguez/containers/octave_6.2.0.sif'
   octave = sing + ' ' +  'exec' + ' ' + sif  + ' '  + 'octave'

   # Nastran launcher
   nastran = 'nastranLaunch'

else:
   octave = 'octave'

   nastran = '/opt/nastran/2019/bin/nast20191'
   nastran_opts = ['old=no', 'batch=no', 'mem=1GB', 'scratch=yes', 'append=yes']
   nastran = [nastran,] + nastran_opts
   #nastran_opts = ' old=no batch=no mem=1GB scratch=yes append=yes'

