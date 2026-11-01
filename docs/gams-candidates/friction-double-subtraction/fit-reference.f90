! Independent MIT-licensed probe; see licenses/directions-fitting-drivers-MIT.txt.
program friction_fit_probe
   use, intrinsic :: iso_fortran_env, only: real64
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   use friction, only: coulomb_model
   use fstats, only: convergence_info
   implicit none
   integer, parameter :: count=12
   type(coulomb_model) :: model
   type(convergence_info) :: info
   real(real64) :: t(count),x(count),v(count),load(count),force(count),modeled(count),residual(count)
   real(real64), parameter :: true_mu=0.375_real64
   integer :: i
   do i=1,count
      t(i)=real(i-1,real64)/16
      x(i)=0
      v(i)=(-1.0_real64)**i
      load(i)=1+real(i,real64)/4
      force(i)=true_mu*load(i)*sign(1.0_real64,v(i))
   end do
   model%friction_coefficient=0.1_real64
   call model%fit(t,x,v,force,load,info=info,fmod=modeled,resid=residual)
   print '(a,2es24.15)', 'True and fitted Coulomb coefficient: ',true_mu,model%friction_coefficient
   print '(a,3l2)', 'Gradient/step/residual convergence: ',info%converge_on_gradient, &
      info%converge_on_solution_change,info%converge_on_residual_parameter
   print '(a,es24.15)', 'Maximum independently recomputed force discrepancy: ', &
      maxval(abs(model%friction_coefficient*load*sign(1.0_real64,v)-force))
   if (.not.ieee_is_finite(model%friction_coefficient)) error stop 'nonfinite fitted parameter'
   if (abs(model%friction_coefficient-true_mu)>1e-7_real64) error stop 'known Coulomb fit differs'
   print '(a)', 'PASS friction-fit-reference'
end program
