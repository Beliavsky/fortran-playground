! Independent MIT consumer; see licenses/transforms-structures-ten-drivers-MIT.txt.
program main
   use iso_fortran_env, only: wp=>real64
   use specialmatrices_strang, only: Strang,solve
   use ieee_arithmetic, only: ieee_is_finite
   implicit none
   type(Strang) :: a
   real(wp),allocatable :: expected(:,:),b(:,:),saved(:,:),actual(:,:),vector(:),residual(:,:)
   integer :: n,pattern,refine,i,j,cases
   cases=0
   do n=2,24
      a=Strang(n); allocate(expected(n,3),b(n,3))
      do pattern=1,3
         do j=1,3
            do i=1,n
               expected(i,j)=real(i*(n+1-i)*j,wp)/16+real(mod(i*j+pattern,7)-3,wp)/8
            end do
         end do
         b=2*expected
         b(2:n,:)=b(2:n,:)-expected(:n-1,:); b(:n-1,:)=b(:n-1,:)-expected(2:n,:)
         saved=b
         do refine=0,1
            actual=solve(a,b,refine=refine==1); vector=solve(a,b(:,1),refine=refine==1)
            residual=2*actual
            residual(2:n,:)=residual(2:n,:)-actual(:n-1,:)
            residual(:n-1,:)=residual(:n-1,:)-actual(2:n,:)
            do j=1,3
               do i=1,n
                  call check(actual(i,j),expected(i,j)); call check(residual(i,j),saved(i,j))
               end do
            end do
            do i=1,n
               call check(vector(i),expected(i,1))
            end do
            if(any(b/=saved)) error stop 'Strang RHS preservation'
            cases=cases+2
         end do
      end do
      deallocate(expected,b)
   end do
   print '(a,i0)', 'SPD tridiagonal vector/multiple-RHS solves, with/without refinement: ',cases
   print '(a)', 'PASS specialmatrices-strang-systems-reference'
contains
   subroutine check(actual,expected)
      real(wp),intent(in) :: actual,expected
      if(.not.ieee_is_finite(actual)) error stop 'Nonfinite result'
      if(abs(actual-expected)>2.e-9_wp*max(1._wp,abs(expected))) error stop 'Independent reference'
   end subroutine
end program
