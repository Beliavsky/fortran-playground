! Independent MIT consumer; see licenses/grids-ten-drivers-MIT.txt.
program main
   use iso_fortran_env, only: real64, int64
   use ieee_arithmetic, only: ieee_is_finite
   use stdlib_math, only: meshgrid, stdlib_meshgrid_ij
   implicit none

   real(real64),allocatable :: x(:),y(:),xx(:,:),yy(:,:),xi(:,:),yi(:,:)
   integer :: nx,ny,i,j,count
   count=0
   do nx=1,7
      do ny=1,6
         allocate(x(nx),y(ny),xx(ny,nx),yy(ny,nx),xi(nx,ny),yi(nx,ny))
         x=[(real(i-4,real64)/2,i=1,nx)]; y=[(real(j+1,real64)/4,j=1,ny)]
         call meshgrid(x,y,xx,yy)
         call meshgrid(x,y,xi,yi,indexing=stdlib_meshgrid_ij)
         do j=1,ny
            do i=1,nx
               call check(xx(j,i),real(i-4,real64)/2)
               call check(yy(j,i),real(j+1,real64)/4)
               call check(xi(i,j),real(i-4,real64)/2)
               call check(yi(i,j),real(j+1,real64)/4)
            end do
         end do
         if(any(x/=[(real(i-4,real64)/2,i=1,nx)])) error stop 'Grid x input preservation'
         if(any(y/=[(real(j+1,real64)/4,j=1,ny)])) error stop 'Grid y input preservation'
         deallocate(x,y,xx,yy,xi,yi)
         count=count+1
      end do
   end do
   print '(a,i0,a)', 'Independent Cartesian rectangles: ',count,'; xy and ij layouts'
   print '(a)', 'PASS stdlib-cartesian-grids-reference'
contains
   subroutine check(actual,expected)
      real(real64),intent(in) :: actual,expected
      if(.not.ieee_is_finite(actual)) error stop 'Nonfinite result'
      if(abs(actual-expected)>3.e-13_real64*max(1._real64,abs(expected))) error stop 'Independent reference'
   end subroutine
end program
