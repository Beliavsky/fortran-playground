! Independent MIT consumer; see licenses/storage-ten-drivers-MIT.txt.
program main
   use iso_fortran_env, only: real64
   use nc4fortran, only: netcdf_file
   use netcdf, only: nf90_open,nf90_close,nf90_nowrite,nf90_inq_varid,nf90_inquire_variable, &
      nf90_inquire_dimension,nf90_get_att,nf90_get_var,nf90_noerr
   implicit none
   type(netcdf_file) :: file
   real(real64),allocatable :: values(:,:),loaded(:,:)
   real(real64) :: cell(1,1)
   integer :: rows,cols,i,j,id,var,dims(2),length,unit,checks
   character(20) :: name,units
   checks=0
   do rows=1,4
      do cols=1,6
         allocate(values(rows,cols),loaded(rows,cols))
         do j=1,cols
            do i=1,rows
               values(i,j)=real(31*i-7*j,real64)/8
            end do
         end do
         call file%open('nc4-fixture.nc',action='w')
         call file%write('field',values,['x','y'])
         call file%write_attribute('field','units','dyadic')
         call file%close()
         ! Cross the convenience wrapper with the native NetCDF Fortran API.
         call check(nf90_open('nc4-fixture.nc',nf90_nowrite,id))
         call check(nf90_inq_varid(id,'field',var))
         call check(nf90_inquire_variable(id,var,dimids=dims))
         call check(nf90_inquire_dimension(id,dims(1),name=name,len=length))
         if(trim(name)/='x' .or. length/=rows) error stop 'x metadata'
         call check(nf90_inquire_dimension(id,dims(2),name=name,len=length))
         if(trim(name)/='y' .or. length/=cols) error stop 'y metadata'
         call check(nf90_get_att(id,var,'units',units))
         if(trim(units)/='dyadic') error stop 'Units'
         do j=1,cols
            do i=1,rows
               call check(nf90_get_var(id,var,cell,start=[i,j],count=[1,1]))
               if(cell(1,1)/=real(31*i-7*j,real64)/8) error stop 'Indexed native value'
               checks=checks+1
            end do
         end do
         call check(nf90_close(id))
         call file%open('nc4-fixture.nc',action='r')
         call file%read('field',loaded)
         call file%close()
         do j=1,cols
            do i=1,rows
               if(loaded(i,j)/=real(31*i-7*j,real64)/8) error stop 'Wrapper value'
            end do
         end do
         open(newunit=unit,file='nc4-fixture.nc',status='old')
         close(unit,status='delete')
         deallocate(values,loaded)
      end do
   end do
   print '(a,i0)', '24 NetCDF4 datasets; native indexed values and wrapper values each: ',checks
   print '(a)', 'PASS nc4-layout-reference'
contains
   subroutine check(rc)
      integer,intent(in) :: rc
      if(rc/=nf90_noerr) error stop 'Native NetCDF API'
   end subroutine
end program
