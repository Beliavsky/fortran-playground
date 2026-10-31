! Original G2h1a1 API driver. MIT: licenses/optimization-api-drivers-MIT.txt.
module objective_problem
   use iso_fortran_env, only: wp=>real64
   use ieee_arithmetic, only: ieee_is_finite
   implicit none
   integer :: evaluations=0
   real(wp),parameter :: lower(2)=[0._wp,0._wp],upper(2)=[1._wp,2._wp]
contains
   subroutine objective(n,x,value)
      integer,intent(in) :: n
      real(wp),intent(in) :: x(:)
      real(wp),intent(out) :: value
      if(n/=2 .or. .not.all(ieee_is_finite(x))) error stop 'invalid BOBYQA callback'
      if(any(x<lower-1.e-12_wp) .or. any(x>upper+1.e-12_wp)) error stop 'callback outside bounds'
      value=(x(1)-2)**2+(x(2)+1)**2
      evaluations=evaluations+1
   end subroutine
end module
program main
   use objective_problem
   use bobyqa_module, only: bobyqa
   implicit none
   real(wp),parameter :: starts(2,3)=reshape([.25_wp,1._wp,.9_wp,.1_wp,.1_wp,1.8_wp],[2,3])
   real(wp) :: x(2),value,gradient(2),projected
   integer :: c
   do c=1,3
      x=starts(:,c)
      evaluations=0
      call bobyqa(2,5,x,lower,upper,.1_wp,1.e-9_wp,0,1000,objective)
      if(evaluations>=1000) error stop 'BOBYQA evaluation budget exhausted'
      if(.not.all(ieee_is_finite(x))) error stop 'nonfinite BOBYQA solution'
      if(maxval(abs(x-[1._wp,0._wp]))>1.e-8_wp) error stop 'known box minimum'
      value=(x(1)-2)**2+(x(2)+1)**2
      if(abs(value-2._wp)>1.e-8_wp) error stop 'known objective'
      gradient=2*(x-[2._wp,-1._wp])
      projected=maxval(abs(x-min(upper,max(lower,x-gradient))))
      if(projected>1.e-8_wp) error stop 'projected optimality residual'
      print '(a,i0,a,2f14.9,a,f14.9,a,i0)', 'Start ',c,': solution=',x,'; f=',value,'; evaluations=',evaluations
   end do
   print '(a)', 'No objective derivatives supplied; reference gradient is used only after solving.'
   print '(a)', 'This API has no returned status flag; checked answers and budget use determine acceptance.'
   print '(a)', 'PASS bobyqa-box-reference'
end program
