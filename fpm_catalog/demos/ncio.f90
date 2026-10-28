program main
   use iso_fortran_env, only: real64
   use ncio, only: nc_create,nc_write_dim,nc_write,nc_read,nc_size
   implicit none
   real(real64) :: original(4),restored(4)
   original=[1._real64,2._real64,4._real64,8._real64]
   call nc_create('sample.nc',description='A small playground NetCDF example')
   call nc_write_dim('sample.nc','x',x=[0._real64,1._real64,2._real64,3._real64],units='m')
   call nc_write('sample.nc','temperature',original,dim1='x',units='K')
   call nc_read('sample.nc','temperature',restored)
   if (nc_size('sample.nc','x')/=4.or.any(restored/=original)) error stop 'NetCDF round trip failed'
   print '(a,4f10.3)', 'Read back temperatures (K):',restored
   print *, 'PASS ncio'
end program
