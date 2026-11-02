! Independent MIT consumer; see licenses/complex-ten-drivers-MIT.txt.
program main
   use iso_fortran_env, only: real64, int64
   use ieee_arithmetic, only: ieee_is_finite
   use stdlib_linalg_constants, only: ilp
   use stdlib_linalg, only: is_square, is_diagonal, is_symmetric, is_skew_symmetric, is_hermitian, &
      is_triangular, is_hessenberg
   implicit none

   real(real64),allocatable :: a(:,:)
   complex(real64),allocatable :: z(:,:)
   integer :: n,i,j,m,count
   logical :: diagonal
   count=0
   do n=1,8
      allocate(a(n,n),z(n,n)); a=0; z=0
      if(.not.is_square(a).or..not.is_diagonal(a).or..not.is_symmetric(a)) error stop 'Zero matrix structure'
      if(.not.is_skew_symmetric(a).or..not.is_hermitian(z)) error stop 'Zero symmetry structure'
      do j=1,n
         do i=1,n
            a=0; z=0; a(i,j)=1; z(i,j)=cmplx(1._real64,1._real64,real64); diagonal=i==j
            if(is_diagonal(a).neqv.diagonal) error stop 'One-hot diagonality'
            if(is_diagonal(z).neqv.diagonal) error stop 'Complex one-hot diagonality'
            if(is_symmetric(a).neqv.diagonal) error stop 'One-hot symmetry'
            if(is_symmetric(z).neqv.diagonal) error stop 'Complex transpose symmetry'
            if(is_skew_symmetric(a).or.is_hermitian(z)) error stop 'One-hot skew/Hermitian rejection'
            if(is_triangular(a,'U').neqv.(i<=j)) error stop 'Upper triangle coordinate'
            if(is_triangular(a,'L').neqv.(i>=j)) error stop 'Lower triangle coordinate'
            if(is_hessenberg(a,'u').neqv.(i<=j+1)) error stop 'Upper Hessenberg coordinate'
            if(is_hessenberg(a,'l').neqv.(i>=j-1)) error stop 'Lower Hessenberg coordinate'
            if(is_triangular(z,'u').neqv.(i<=j)) error stop 'Complex upper triangle'
            if(is_hessenberg(z,'L').neqv.(i>=j-1)) error stop 'Complex lower Hessenberg'
            count=count+1
         end do
      end do
      if(n>=2) then
         a=0; a(1,n)=2; a(n,1)=2
         if(.not.is_symmetric(a).or.is_skew_symmetric(a)) error stop 'Positive symmetric pair'
         a(n,1)=-2
         if(.not.is_skew_symmetric(a).or.is_symmetric(a)) error stop 'Positive skew pair'
         z=0; z(1,n)=cmplx(1._real64,2._real64,real64); z(n,1)=cmplx(1._real64,-2._real64,real64)
         if(.not.is_hermitian(z).or.is_symmetric(z)) error stop 'Genuinely complex Hermitian pair'
      end if
      deallocate(a,z)
   end do
   do m=1,7
      do n=1,6
         allocate(a(m,n)); a=0
         if(is_square(a).neqv.(m==n)) error stop 'Rectangular squareness'
         deallocate(a)
      end do
   end do
   print '(a,i0,a)', 'Matrix-structure one-hot positions: ',count,'; seven predicates and 42 rectangular shapes'
   print '(a)', 'PASS stdlib-matrix-structure-reference'
end program
