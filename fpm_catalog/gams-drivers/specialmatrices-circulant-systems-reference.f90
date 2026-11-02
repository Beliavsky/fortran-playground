! Independent MIT consumer; see licenses/transforms-structures-ten-drivers-MIT.txt.
program main
   use iso_fortran_env, only: wp=>real64
   use specialmatrices_circulant, only: Circulant,solve
   use ieee_arithmetic, only: ieee_is_finite
   implicit none
   type(Circulant) :: a
   real(wp),allocatable :: c(:),matrix(:,:),expected(:,:),b(:,:),saved(:,:),actual(:,:),vector(:),residual(:,:)
   integer :: n,pattern,i,j,cases
   cases=0
   do n=2,23
      allocate(c(n),matrix(n,n),expected(n,3))
      do pattern=1,3
         do i=2,n
            c(i)=real((-1)**i*(1+mod(i*i+pattern,7)),wp)/32
         end do
         c(1)=2+sum(abs(c(2:n))); a=Circulant(c)
         do j=1,n
            do i=1,n
               matrix(i,j)=c(modulo(i-j,n)+1)
            end do
         end do
         do j=1,3
            do i=1,n
               expected(i,j)=real(i-j,wp)/4+real(mod(i*j+pattern,7),wp)/16
            end do
         end do
         b=matmul(matrix,expected); saved=b
         actual=solve(a,b); vector=solve(a,b(:,1)); residual=matmul(matrix,actual)
         do j=1,3
            do i=1,n
               call check(actual(i,j),expected(i,j)); call check(residual(i,j),saved(i,j))
            end do
         end do
         do i=1,n
            call check(vector(i),expected(i,1))
         end do
         if(any(b/=saved)) error stop 'Circulant RHS preservation'
         cases=cases+2
      end do
      deallocate(c,matrix,expected)
   end do
   print '(a,i0)', 'Strictly diagonally dominant circulant vector/multiple-RHS systems: ',cases
   print '(a)', 'PASS specialmatrices-circulant-systems-reference'
contains
   subroutine check(actual,expected)
      real(wp),intent(in) :: actual,expected
      if(.not.ieee_is_finite(actual)) error stop 'Nonfinite result'
      if(abs(actual-expected)>2.e-9_wp*max(1._wp,abs(expected))) error stop 'Independent reference'
   end subroutine
end program
