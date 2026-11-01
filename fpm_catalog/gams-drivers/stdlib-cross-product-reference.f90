! Independent MIT consumer; see licenses/pca-ordering-ten-drivers-MIT.txt.
program main
   use iso_fortran_env, only: real64, int32, int64
   use ieee_arithmetic, only: ieee_is_finite
   use stdlib_linalg, only: cross_product
   implicit none
   real(real64) :: a(3),b(3),actual(3),expected(3)
   integer :: i,j,t,u,calls
   calls=0
   do i=1,3
      a=0; a(i)=1
      do j=1,3
         b=0; b(j)=1
         call check_pair()
      end do
   end do
   do t=-32,32
      do u=-16,16
         a=real([t,u,t-u],real64)/8
         b=real([u,-t,t+u],real64)/16
         call check_pair()
      end do
   end do
   print '(a,i0)', 'Cross products versus Levi-Civita determinant sums, antisymmetry and orthogonality: ',calls
   print '(a)', 'PASS stdlib-cross-product-reference'
contains
   subroutine check_pair()
      integer :: p,q,r,epsilon
      expected=0
      do p=1,3
         do q=1,3
            do r=1,3
               epsilon=((p-q)*(q-r)*(r-p))/2
               expected(p)=expected(p)+epsilon*a(q)*b(r)
            end do
         end do
      end do
      actual=cross_product(a,b)
      if(.not.all(ieee_is_finite(actual))) error stop 'Nonfinite cross product'
      if(any(actual/=expected)) error stop 'Independent determinant sum'
      if(any(actual+cross_product(b,a)/=0)) error stop 'Cross-product antisymmetry'
      if(dot_product(actual,a)/=0.or.dot_product(actual,b)/=0) error stop 'Cross-product orthogonality'
      calls=calls+1
   end subroutine
end program
