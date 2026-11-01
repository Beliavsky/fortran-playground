! Independent MIT consumer; see licenses/systems-spectra-ten-drivers-MIT.txt.
program main
   use iso_fortran_env, only: real64
   use ieee_arithmetic, only: ieee_is_finite
   use stdlib_linalg_iterative_solvers, only: stdlib_solve_cg
   implicit none
   real(real64),allocatable :: a(:,:),saved(:,:),b(:),x(:),expected(:),d(:)
   real(real64) :: value,residual,scale
   integer :: n,t,i,j,calls
   calls=0
   do n=2,18
      allocate(a(n,n),saved(n,n),b(n),x(n),expected(n),d(n))
      do t=1,6
         do i=1,n
            expected(i)=(-1._real64)**i*(i+t)/16
            d(i)=1
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
         call stdlib_solve_cg(a,b,x,rtol=1.e-12_real64,atol=1.e-14_real64, &
              maxiter=10*n,restart=.false.)
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
         if(any(a/=saved)) error stop 'Iterative matrix preservation'
         calls=calls+1
      end do
      deallocate(a,saved,b,x,expected,d)
   end do
   print '(a,i0)', 'Dense known-solution systems, orders 2..18, nonzero initial guess, independently recomputed residuals: ',calls
   print '(a)', 'PASS stdlib-cg-reference'
end program
