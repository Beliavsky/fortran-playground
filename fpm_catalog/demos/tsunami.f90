! Uses the unmodified serial Chapter 4 modules from modern-fortran/tsunami (MIT).
! The time-stepping equations follow src/ch04/tsunami.f90. No coarrays are used.
program main
   use iso_fortran_env, only: real32, real64
   use ieee_arithmetic, only: ieee_is_finite
   use mod_diff, only: diff_centered, diff_upwind
   use mod_initial, only: set_gaussian
   implicit none
   integer, parameter :: n=100, steps=200
   real(real32), parameter :: dt=0.02_real32, dx=1.0_real32, g=9.8_real32, depth=10.0_real32
   real(real32) :: h(n), u(n), initial(n), wave(n), expected(n), calculated(n)
   real(real32) :: pi, angle, phase
   real(real64) :: mass_initial, mass_final
   integer :: i, k, left
   pi=acos(-1.0_real32)
   phase=2*pi/real(n,real32)
   do i=1,n
      angle=phase*real(i-1,real32)
      wave(i)=sin(angle)
      expected(i)=sin(phase)*cos(angle)
   end do
   calculated=diff_centered(wave)
   if (maxval(abs(calculated-expected)) > 1.0e-6_real32) error stop 'Centered difference check'
   do i=1,n
      left=modulo(i-2,n)+1
      expected(i)=wave(i)-wave(left)
   end do
   calculated=diff_upwind(wave)
   if (maxval(abs(calculated-expected)) > 1.0e-6_real32) error stop 'Upwind difference check'
   call set_gaussian(h,25,0.02_real32)
   if (abs(h(25)-1.0_real32) > epsilon(1.0_real32)) error stop 'Gaussian peak check'
   if (maxval(abs(h(24:1:-1)-h(26:49))) > 1.0e-6_real32) error stop 'Gaussian symmetry check'
   h=0.1_real32*h
   initial=h
   u=0
   mass_initial=sum(real(h,real64))*real(dx,real64)
   do k=1,steps
      u=u-(u*diff_centered(u)+g*diff_centered(h))/dx*dt
      h=h-diff_centered(u*(depth+h))/dx*dt
      if (.not.all(ieee_is_finite(h)) .or. .not.all(ieee_is_finite(u))) error stop 'Nonfinite solution'
   end do
   mass_final=sum(real(h,real64))*real(dx,real64)
   if (abs(mass_final-mass_initial)>1.0e-5_real64*mass_initial) error stop 'Mass conservation check'
   if (maxval(abs(h-initial))<1.0e-3_real32) error stop 'Wave did not evolve'
   if (minval(depth+h)<=0.0_real32) error stop 'Nonpositive total water depth'
   print '(a,i0)', 'Time steps: ',steps
   print '(a,2f13.8)', 'Initial and final integrated elevation: ',mass_initial,mass_final
   print '(a,es12.4)', 'Absolute conservation error: ',abs(mass_final-mass_initial)
   print '(a,2f12.7)', 'Final elevation range: ',minval(h),maxval(h)
   print '(a)', 'PASS tsunami'
end program main
