! Original H2b1a2 API driver. MIT: licenses/applied-methods-drivers-MIT.txt.
module problem
   use iso_fortran_env, only: dp=>real64
   implicit none
   integer :: powers(3)=0,domain=1
contains
   function integrand(x) result(value)
      real(dp),intent(in) :: x(:)
      real(dp) :: value
      value=product(x**powers(:size(x)))
   end function
   function bounds(x,dimension) result(interval)
      real(dp),intent(in) :: x(:)
      integer,intent(in) :: dimension
      real(dp) :: interval(2)
      select case(domain)
      case(1)
         if(dimension==1) then
            interval=[-1._dp,2._dp]
         else
            interval=[0._dp,3._dp]
         end if
      case(2)
         interval=[0._dp,1._dp]
         if(dimension==2) interval(2)=1+x(1)**2
      case(3)
         select case(dimension)
         case(1)
            interval=[-1._dp,1._dp]
         case(2)
            interval=[0._dp,2._dp]
         case(3)
            interval=[1._dp,3._dp]
         end select
      end select
   end function
end module
program main
   use problem
   use gauss_leg_mod, only: gauss_leg_nd
   use ieee_arithmetic, only: ieee_is_finite
   implicit none
   real(dp) :: actual,expected,choose,error,maximum_error
   integer :: p,q,r,panels,cases
   maximum_error=0; cases=0
   domain=1
   do p=0,4
      do q=0,4
         powers=[p,q,0]
         expected=(2._dp**(p+1)-(-1._dp)**(p+1))/(p+1)*3._dp**(q+1)/(q+1)
         do panels=1,2
            actual=gauss_leg_nd([panels,panels],integrand,bounds)
            call check(actual,expected)
         end do
      end do
   end do
   domain=2
   do p=0,3
      do q=0,3
         powers=[p,q,0]
         expected=0; choose=1
         ! Integrate x^p*(1+x^2)^(q+1)/(q+1) exactly by the binomial theorem.
         do r=0,q+1
            expected=expected+choose/real((q+1)*(p+2*r+1),dp)
            choose=choose*(q+1-r)/real(r+1,dp)
         end do
         actual=gauss_leg_nd([1,1],integrand,bounds)
         call check(actual,expected)
      end do
   end do
   domain=3; powers=[2,3,1]
   actual=gauss_leg_nd([1,1,1],integrand,bounds)
   call check(actual,32._dp/3)
   if(cases/=67) error stop 'case count'
   print '(a,f22.14)', '3D integral of x^2*y^3*z: ',actual
   print '(a,i0)', 'Exact polynomial integral checks: ',cases
   print '(a,es14.5)', 'Maximum scaled error: ',maximum_error
   print '(a)', 'Panel counts are explicit; each panel uses six Gauss-Legendre nodes per dimension.'
   print '(a)', 'PASS integrate-nd-polynomial-reference'
contains
   subroutine check(value,reference)
      real(dp),intent(in) :: value,reference
      if(.not.ieee_is_finite(value)) error stop 'nonfinite quadrature result'
      error=abs(value-reference)/max(1._dp,abs(reference))
      maximum_error=max(maximum_error,error)
      if(error>1.e-11_dp) error stop 'exact polynomial integral'
      cases=cases+1
   end subroutine
end program
