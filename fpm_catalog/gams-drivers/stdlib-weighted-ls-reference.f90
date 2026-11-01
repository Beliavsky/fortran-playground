! Independent MIT consumer; see licenses/systems-spectra-ten-drivers-MIT.txt.
program main
   use iso_fortran_env, only: real64
   use ieee_arithmetic, only: ieee_is_finite
   use stdlib_linalg, only: solve_weighted_lstsq
   use stdlib_linalg_state, only: linalg_state_type
   implicit none
   real(real64),allocatable :: a(:,:),saved(:,:),w(:),b(:)
   real(real64) :: x(2),expected(2),sw,sx,sxx,sy,sxy,delta,r0,r1,t
   type(linalg_state_type) :: err
   integer :: n,j,k
   do n=4,15
      allocate(a(n,2),saved(n,2),w(n),b(n))
      do k=1,8
         sw=0; sx=0; sxx=0; sy=0; sxy=0
         do j=1,n
            t=real(2*j-n-1,real64)/n
            a(j,:)=[1._real64,t]
            w(j)=real(1+mod(j*k,16),real64)
            b(j)=real(k-4,real64)/4+0.75_real64*t+t*t/4+(-1._real64)**j/16
            sw=sw+w(j); sx=sx+w(j)*t; sxx=sxx+w(j)*t*t
            sy=sy+w(j)*b(j); sxy=sxy+w(j)*t*b(j)
         end do
         delta=sw*sxx-sx*sx
         expected=[(sy*sxx-sx*sxy)/delta,(sw*sxy-sx*sy)/delta]
         saved=a
         call solve_weighted_lstsq(w,a,b,x,err=err)
         if(.not.err%ok()) error stop 'Weighted least-squares status'
         if(.not.all(ieee_is_finite(x))) error stop 'Nonfinite weighted solution'
         if(maxval(abs(x-expected))>5.e-12_real64) error stop 'Independent weighted coefficients'
         r0=0; r1=0
         do j=1,n
            t=x(1)+x(2)*saved(j,2)-b(j)
            r0=r0+w(j)*t; r1=r1+w(j)*saved(j,2)*t
         end do
         if(max(abs(r0),abs(r1))>5.e-12_real64*sw) error stop 'Weighted normal equations'
         if(any(a/=saved)) error stop 'Weighted matrix preservation'
      end do
      deallocate(a,saved,w,b)
   end do
   print '(a)', '96 weighted line fits versus independent scalar-sum formulas and weighted normal equations'
   print '(a)', 'PASS stdlib-weighted-ls-reference'
end program
