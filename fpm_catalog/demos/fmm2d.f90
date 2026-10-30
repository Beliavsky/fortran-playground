! Real 2D Laplace potentials: compare the FMM with an independent log-distance sum.
program main
   use, intrinsic :: iso_fortran_env, only: real64
   implicit none
   integer, parameter :: ns=512, nt=16
   real(real64) :: sources(2,ns), charge(ns), targets(2,nt), potential(nt), direct(nt)
   real(real64) :: distance, relative_error
   integer :: i, j, status
   interface
      subroutine rfmm2d_t_c_p(eps,ns,sources,charge,nt,targ,pottarg,ier)
         import real64
         integer :: ns, nt, ier
         real(real64) :: eps, sources(2,ns), charge(ns), targ(2,nt), pottarg(nt)
      end subroutine rfmm2d_t_c_p
   end interface
   do i=1,ns
      sources(:,i) = [real(mod(i-1,32),real64)/31.0_real64, &
         real((i-1)/32,real64)/15.0_real64]
      charge(i) = (1.0_real64+0.3_real64*sin(real(i,real64)))/real(ns,real64)
   end do
   do i=1,nt
      targets(:,i) = [1.25_real64+0.03_real64*i, 0.05_real64*i]
   end do
   call rfmm2d_t_c_p(1.0e-10_real64,ns,sources,charge,nt,targets,potential,status)
   if (status /= 0) error stop 'FMM2D failed'
   direct = 0.0_real64
   do i=1,nt
      do j=1,ns
         distance = sqrt(sum((targets(:,i)-sources(:,j))**2))
         direct(i) = direct(i)+charge(j)*log(distance)
      end do
   end do
   relative_error = maxval(abs(potential-direct))/maxval(abs(direct))
   print '(a,i0,a,i0)', 'Sources: ', ns, '; targets: ', nt
   print '(a,es12.4)', 'Relative maximum error against direct summation: ', relative_error
   print '(a,es16.8)', 'First target potential: ', potential(1)
   if (relative_error > 1.0e-8_real64) error stop 'Incorrect 2D potentials'
   print '(a)', 'PASS fmm2d'
end program main
