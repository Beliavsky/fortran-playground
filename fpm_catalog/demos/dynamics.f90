! Frequency response of m*x''+c*x'+k*x=cos(omega*t).
module playground_dynamics_force
   use, intrinsic :: iso_fortran_env, only: real64
   implicit none
contains
   subroutine unit_force(frequency,force,args)
      real(real64),intent(in) :: frequency
      complex(real64),intent(out) :: force(:)
      class(*),optional,intent(inout) :: args
      force=cmplx(1._real64,0._real64,real64)
   end subroutine
end module
program demo_dynamics
   use playground_dynamics_force
   use dynamics, only: frf,frequency_response,modal_excite
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   implicit none
   real(real64),parameter :: omega(*)=[0._real64,0.5_real64,1._real64,1.5_real64, &
      2._real64,2.5_real64,3._real64,4._real64]
   real(real64) :: mass(1,1),stiffness(1,1),err
   complex(real64) :: exact
   type(frf) :: response
   procedure(modal_excite),pointer :: forcing
   integer :: i
   mass=1; stiffness=4
   forcing=>unit_force
   ! C=alpha*M+beta*K, so alpha=0.2 and beta=0 give damping c=0.2.
   response=frequency_response(mass,stiffness,0.2_real64,0._real64,omega,forcing)
   if (.not.allocated(response%responses)) error stop 'No frequency response'
   if (size(response%responses,1)/=size(omega)) error stop 'Wrong frequency count'
   if (.not.all(ieee_is_finite(abs(response%responses)))) error stop 'Nonfinite response'
   print '(a)', 'Angular frequency    Displacement amplitude    Analytic error'
   do i=1,size(omega)
      exact=1/cmplx(4-omega(i)**2,0.2_real64*omega(i),real64)
      err=abs(response%responses(i,1)-exact)
      print '(f14.5,f26.12,es18.3)',omega(i),abs(response%responses(i,1)),err
      if (err>1e-10_real64) error stop 'Frequency response differs from analytic solution'
   end do
   print '(a)', 'PASS dynamics'
end program
