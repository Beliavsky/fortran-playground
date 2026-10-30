! A self-contained NetCDF classic write/read round trip.
program main
   use netcdf
   implicit none
   integer :: ncid, xdim, ydim, variable, dims(2), i, j, length, unit, status
   real :: values(3,2), loaded(3,2)
   character(len=20) :: units
   do j = 1, 2
      do i = 1, 3
         values(i,j) = real(i + 10*j)
      end do
   end do
   call check(nf90_create('dataset.nc', nf90_clobber, ncid))
   call check(nf90_def_dim(ncid, 'x', 3, xdim))
   call check(nf90_def_dim(ncid, 'y', 2, ydim))
   call check(nf90_def_var(ncid, 'temperature', nf90_float, [xdim,ydim], variable))
   call check(nf90_put_att(ncid, variable, 'units', 'degree_Celsius'))
   call check(nf90_enddef(ncid))
   call check(nf90_put_var(ncid, variable, values))
   call check(nf90_close(ncid))
   call check(nf90_open('dataset.nc', nf90_nowrite, ncid))
   call check(nf90_inq_varid(ncid, 'temperature', variable))
   call check(nf90_inquire_variable(ncid, variable, dimids=dims))
   call check(nf90_inquire_dimension(ncid, dims(1), len=length))
   if (length /= 3) error stop 'x dimension mismatch'
   call check(nf90_inquire_dimension(ncid, dims(2), len=length))
   if (length /= 2) error stop 'y dimension mismatch'
   call check(nf90_get_att(ncid, variable, 'units', units))
   if (trim(units) /= 'degree_Celsius') error stop 'attribute mismatch'
   call check(nf90_get_var(ncid, variable, loaded))
   if (any(abs(loaded-values) > 1.0e-6)) error stop 'array mismatch'
   call check(nf90_close(ncid))
   print '(a,a)', 'Units: ', trim(units)
   do j = 1, 2
      print '(3f8.1)', loaded(:,j)
   end do
   open(newunit=unit, file='dataset.nc', status='old', iostat=status)
   if (status /= 0) error stop 'cleanup open failed'
   close(unit, status='delete')
   print '(a)', 'PASS netcdf-fortran'
contains
   subroutine check(code)
      integer, intent(in) :: code
      if (code /= nf90_noerr) then
         print '(a)', trim(nf90_strerror(code))
         error stop 'NetCDF operation failed'
      end if
   end subroutine check
end program main
