! Independent MIT consumer; see licenses/systems-spectra-ten-drivers-MIT.txt.
module driver_operators
   use iso_fortran_env, only: real64
   implicit none
   real(real64),allocatable :: matrix(:,:),inverse_diagonal(:)
contains
   subroutine multiply(x,y,alpha,beta,op)
      real(real64),intent(in) :: x(:),alpha,beta
      real(real64),intent(inout) :: y(:)
      character(1),intent(in) :: op
      if(op/='N') error stop 'Unverified operator request'
      y=alpha*matmul(matrix,x)+beta*y
   end subroutine
   subroutine precondition(x,y,alpha,beta,op)
      real(real64),intent(in) :: x(:),alpha,beta
      real(real64),intent(inout) :: y(:)
      character(1),intent(in) :: op
      if(op/='N') error stop 'Unverified preconditioner request'
      y=alpha*inverse_diagonal*x+beta*y
   end subroutine
end module
program main
   use iso_fortran_env, only: real64
   use ieee_arithmetic, only: ieee_is_finite
   use stdlib_linalg_iterative_solvers, only: stdlib_solve_pcg_kernel
   use stdlib_linalg_iterative_solvers, only: stdlib_linop_dp_type, stdlib_solver_workspace_dp_type
   use driver_operators, only: matrix, inverse_diagonal, multiply, precondition
   implicit none
   type(stdlib_linop_dp_type) :: operator, preconditioner
   type(stdlib_solver_workspace_dp_type) :: workspace
   real(real64),allocatable :: a(:,:),saved(:,:),b(:),x(:),expected(:),d(:)
   real(real64) :: value,residual,scale
   integer :: n,t,i,j,calls
   calls=0
   operator%matvec=>multiply
   preconditioner%matvec=>precondition
   do n=2,18
      allocate(a(n,n),saved(n,n),b(n),x(n),expected(n),d(n))
      allocate(matrix(n,n),inverse_diagonal(n),workspace%tmp(n,4))
      do t=1,6
         do i=1,n
            expected(i)=(-1._real64)**i*(i+t)/16
            d(i)=1
         end do
         do i=1,n
            d(i)=10._real64**(2._real64*(i-1)/(n-1)-1)
         end do
         do i=1,n
            do j=1,n
               value=real(i*j,real64)/(100*n*n)
               if(i==j) value=value+2+real(i+t,real64)/16
               if(abs(i-j)==1) value=value-0.3_real64
               a(i,j)=d(i)*value*d(j)
            end do
         end do
         b=0
         do i=1,n
            do j=1,n
               b(i)=b(i)+a(i,j)*expected(j)
            end do
         end do
         x=0.125_real64
         saved=a
         matrix=a
         workspace%tmp=0
         inverse_diagonal=1
         do i=1,n
            inverse_diagonal(i)=1/a(i,i)
         end do
         call stdlib_solve_pcg_kernel(operator,preconditioner,b,x,rtol=1.e-12_real64,atol=1.e-14_real64, &
              maxiter=10*n,workspace=workspace)
         if(.not.all(ieee_is_finite(x))) error stop 'Nonfinite iterative solution'
         scale=max(1._real64,maxval(abs(expected)))
         if(maxval(abs(x-expected))>2.e-9_real64*scale) error stop 'Manufactured iterative solution'
         do i=1,n
            residual=-b(i)
            do j=1,n
               residual=residual+saved(i,j)*x(j)
            end do
            if(abs(residual)>2.e-9_real64*max(1._real64,maxval(abs(b)))) error stop 'Recomputed scalar residual'
         end do
         if(any(matrix/=saved)) error stop 'Iterative matrix preservation'
         calls=calls+1
      end do
      deallocate(a,saved,b,x,expected,d,matrix,inverse_diagonal,workspace%tmp)
   end do
   print '(a,i0)', 'Dense known-solution systems, orders 2..18, nonzero initial guess, independently recomputed residuals: ',calls
   print '(a)', 'PASS stdlib-pcg-kernel-reference'
end program
