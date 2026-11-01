! Independent MIT consumer; see licenses/storage-ten-drivers-MIT.txt.
program main
   use netcdf
   implicit none
   integer :: n,m,i,j,id,dx,dy,var,dims(2),length,unit,checks
   real,allocatable :: values(:,:),loaded(:,:)
   real :: cell(1,1),update(1,1)
   character(4) :: magic
   character(20) :: name,units
   checks=0
   do n=1,4
      do m=1,6
         allocate(values(n,m),loaded(n,m))
         do j=1,m
            do i=1,n
               values(i,j)=real(11*i-3*j)/8
            end do
         end do
         call check(nf90_create('classic.nc',nf90_clobber,id))
         call check(nf90_def_dim(id,'row',n,dx))
         call check(nf90_def_dim(id,'column',m,dy))
         call check(nf90_def_var(id,'field',nf90_float,[dx,dy],var))
         call check(nf90_put_att(id,var,'units','dyadic'))
         call check(nf90_enddef(id))
         call check(nf90_put_var(id,var,values))
         update(1,1)=-999.5
         call check(nf90_put_var(id,var,update,start=[n,m],count=[1,1]))
         call check(nf90_close(id))
         open(newunit=unit,file='classic.nc',status='old',access='stream',form='unformatted')
         read(unit) magic
         close(unit)
         if(magic/='CDF'//achar(1)) error stop 'Classic format magic'
         call check(nf90_open('classic.nc',nf90_nowrite,id))
         call check(nf90_inq_varid(id,'field',var))
         call check(nf90_inquire_variable(id,var,dimids=dims))
         call check(nf90_inquire_dimension(id,dims(1),name=name,len=length))
         if(trim(name)/='row'.or.length/=n) error stop 'Row metadata'
         call check(nf90_inquire_dimension(id,dims(2),name=name,len=length))
         if(trim(name)/='column'.or.length/=m) error stop 'Column metadata'
         call check(nf90_get_att(id,var,'units',units))
         if(trim(units)/='dyadic') error stop 'Units'
         call check(nf90_get_var(id,var,loaded))
         do j=1,m
            do i=1,n
               call check(nf90_get_var(id,var,cell,start=[i,j],count=[1,1]))
               if(i==n.and.j==m) then
                  if(cell(1,1)/=-999.5.or.loaded(i,j)/=-999.5) error stop 'Updated cell'
               else
                  if(cell(1,1)/=real(11*i-3*j)/8) error stop 'Indexed cell'
                  if(loaded(i,j)/=real(11*i-3*j)/8) error stop 'Full array cell'
               end if
               checks=checks+2
            end do
         end do
         call check(nf90_close(id))
         open(newunit=unit,file='classic.nc',status='old')
         close(unit,status='delete')
         deallocate(values,loaded)
      end do
   end do
   print '(a,i0)', '24 classic files; exact full/indexed values after one-cell update: ',checks
   print '(a)', 'PASS netcdf-slices-reference'
contains
   subroutine check(rc)
      integer,intent(in) :: rc
      if(rc/=nf90_noerr) error stop 'NetCDF API'
   end subroutine
end program
