! 3D Laplace potentials use the library normalization 1/(4*pi*r).
! FMM3D's classic interface requires 64-bit source counts and status values.
program main
   use, intrinsic :: iso_fortran_env, only: real64, int64
   implicit none
   integer(int64), parameter :: ns=1024_int64, nt=16_int64
   real(real64) :: sources(3,ns), charge(ns), targets(3,nt), potential(nt), direct(nt)
   real(real64) :: distance, relative_error
   real(real64), parameter :: pi=acos(-1.0_real64)
   integer(int64) :: status
   integer :: i, j
   interface
      subroutine lfmm3d_t_c_p(eps,ns,sources,charge,nt,targ,pottarg,ier)
         import real64, int64
         integer(int64) :: ns, nt, ier
         real(real64) :: eps, sources(3,ns), charge(ns), targ(3,nt), pottarg(nt)
      end subroutine lfmm3d_t_c_p
   end interface
   do i=1,int(ns)
      sources(:,i) = [real(mod(i-1,16),real64)/15.0_real64, &
         real(mod((i-1)/16,8),real64)/7.0_real64, real((i-1)/128,real64)/7.0_real64]
      charge(i) = (1.0_real64+0.3_real64*sin(real(i,real64)))/real(ns,real64)
   end do
   do i=1,int(nt)
      targets(:,i) = [1.25_real64+0.03_real64*i, 0.05_real64*i, 0.04_real64*i]
   end do
   call lfmm3d_t_c_p(1.0e-10_real64,ns,sources,charge,nt,targets,potential,status)
   if (status /= 0_int64) error stop 'FMM3D failed'
   direct = 0.0_real64
   do i=1,int(nt)
      do j=1,int(ns)
         distance = sqrt(sum((targets(:,i)-sources(:,j))**2))
         direct(i) = direct(i)+charge(j)/(4.0_real64*pi*distance)
      end do
   end do
   relative_error = maxval(abs(potential-direct))/maxval(abs(direct))
   print '(a,i0,a,i0)', 'Sources: ', ns, '; targets: ', nt
   print '(a,es12.4)', 'Relative maximum error against direct summation: ', relative_error
   print '(a,es16.8)', 'First target potential: ', potential(1)
   if (relative_error > 1.0e-8_real64) error stop 'Incorrect 3D potentials'
   print '(a)', 'PASS fmm3d'
end program main
