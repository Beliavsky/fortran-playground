! Independent MIT consumer; see licenses/storage-ten-drivers-MIT.txt.
program main
   use iso_fortran_env, only: real64
   use iso_c_binding, only: c_int,c_char,c_size_t,c_double,c_null_char
   use nc4fortran, only: netcdf_file
   implicit none
   interface
      integer(c_int) function nc_open(path,mode,id) bind(c)
         import c_int,c_char
         character(c_char),intent(in) :: path(*)
         integer(c_int),value :: mode
         integer(c_int),intent(out) :: id
      end function
      integer(c_int) function nc_close(id) bind(c)
         import c_int
         integer(c_int),value :: id
      end function
      integer(c_int) function nc_inq_varid(id,name,var) bind(c)
         import c_int,c_char
         integer(c_int),value :: id
         character(c_char),intent(in) :: name(*)
         integer(c_int),intent(out) :: var
      end function
      integer(c_int) function nc_inq_dimid(id,name,dim) bind(c)
         import c_int,c_char
         integer(c_int),value :: id
         character(c_char),intent(in) :: name(*)
         integer(c_int),intent(out) :: dim
      end function
      integer(c_int) function nc_inq_dimlen(id,dim,length) bind(c)
         import c_int,c_size_t
         integer(c_int),value :: id,dim
         integer(c_size_t),intent(out) :: length
      end function
      integer(c_int) function nc_inq_vardimid(id,var,dims) bind(c)
         import c_int
         integer(c_int),value :: id,var
         integer(c_int),intent(out) :: dims(*)
      end function
      integer(c_int) function nc_get_var1_double(id,var,index,value) bind(c)
         import c_int,c_size_t,c_double
         integer(c_int),value :: id,var
         integer(c_size_t),intent(in) :: index(*)
         real(c_double),intent(out) :: value
      end function
   end interface
   type(netcdf_file) :: file
   real(real64),allocatable :: values(:,:),loaded(:,:)
   real(c_double) :: cell
   integer :: rows,cols,i,j,unit,checks
   integer(c_int) :: id,var,dims(2),xdim,ydim
   integer(c_size_t) :: length
   character(20) :: units
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
         ! Cross the wrapper with the C API: reversed axes and zero-based indices.
         call check(nc_open('nc4-fixture.nc'//c_null_char,0_c_int,id))
         call check(nc_inq_varid(id,'field'//c_null_char,var))
         call check(nc_inq_dimid(id,'x'//c_null_char,xdim))
         call check(nc_inq_dimid(id,'y'//c_null_char,ydim))
         call check(nc_inq_dimlen(id,xdim,length))
         if(length/=rows) error stop 'x metadata'
         call check(nc_inq_dimlen(id,ydim,length))
         if(length/=cols) error stop 'y metadata'
         call check(nc_inq_vardimid(id,var,dims))
         if(any(dims/=[ydim,xdim])) error stop 'Native C axis order'
         do j=1,cols
            do i=1,rows
               call check(nc_get_var1_double(id,var,int([j-1,i-1],c_size_t),cell))
               if(cell/=real(31*i-7*j,real64)/8) error stop 'Indexed native value'
               checks=checks+1
            end do
         end do
         call check(nc_close(id))
         call file%open('nc4-fixture.nc',action='r')
         call file%read('field',loaded)
         call file%read_attribute('field','units',units)
         call file%close()
         if(trim(units)/='dyadic') error stop 'Units'
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
      if(rc/=0) error stop 'Native NetCDF API'
   end subroutine
end program
