! Independent MIT consumer; see licenses/statistics-services-ten-drivers-MIT.txt.
program main
   use iso_fortran_env, only: real64
   use ieee_arithmetic, only: ieee_is_finite
   use stdlib_stats, only: cov
   implicit none
   real(real64),allocatable :: x(:,:)
   real(real64) :: pair(3,3),expected(3,3),actual(3,3)
   integer :: n,k,l,i,j,c,checks
   checks=0
   do n=4,32
      allocate(x(n,3))
      do j=1,3
         do k=1,n
            x(k,j)=real(mod(k*j+3*j,11)-5,real64)/8+real((j-2)*k,real64)/16
         end do
      end do
      pair=0
      ! Pairwise differences avoid calling mean, variance, covariance or MATMUL.
      do j=1,3
         do i=1,3
            do l=2,n
               do k=1,l-1
                  pair(i,j)=pair(i,j)+(x(k,i)-x(l,i))*(x(k,j)-x(l,j))
               end do
            end do
         end do
      end do
      do c=0,1
         expected=pair/real(n*(n-c),real64)
         actual=cov(x,dim=1,corrected=(c==1))
         call verify()
         actual=cov(transpose(x),dim=2,corrected=(c==1))
         call verify()
      end do
      deallocate(x)
   end do
   print '(a,i0)', '29 datasets; sample/population covariance and both axis conventions; entries: ',checks
   print '(a)', 'PASS stdlib-covariance-reference'
contains
   subroutine verify()
      if(.not.all(ieee_is_finite(actual))) error stop 'Nonfinite covariance'
      if(any(abs(actual-expected)>2.e-12_real64*max(1._real64,abs(expected)))) error stop 'Pairwise oracle'
      checks=checks+9
   end subroutine
end program
