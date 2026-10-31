! Independent API consumer; see licenses/adaptive-ad-drivers-MIT.txt.
module derivative_reference_functions
   use differentia
   implicit none
   integer :: degree=0, expression=1
contains
   function monomial(x) result(y)
      type(dual), intent(in) :: x
      type(dual) :: y
      if (degree==0) then
         y=0*x+3 ! Lift the constant into the seeded dual space.
      else
         y=x**degree
      end if
   end function monomial
   function composite(x) result(y)
      type(dual), intent(in) :: x
      type(dual) :: y
      select case(expression)
      case(1)
         y=1/(1+x*x)
      case(2)
         y=exp(sin(x))
      case(3)
         y=log(2+x)
      case(4)
         y=sqrt(2+x)
      case(5)
         y=sin(2*x)*cos(x)
      case(6)
         y=atan(x)
      case(7)
         y=tan(0.5_wp*x)
      case(8)
         y=(2+x)**1.5_wp
      case(9)
         y=2.0_wp**x
      case(10)
         y=(2+x)**(1+0.25_wp*x)
      case(11)
         y=asin(x/2)
      case(12)
         y=acos(x/2)
      end select
   end function composite
   subroutine reference(x,y,dy)
      real(wp), intent(in) :: x
      real(wp), intent(out) :: y,dy
      select case(expression)
      case(1)
         y=1/(1+x*x); dy=-2*x/(1+x*x)**2
      case(2)
         y=exp(sin(x)); dy=y*cos(x)
      case(3)
         y=log(2+x); dy=1/(2+x)
      case(4)
         y=sqrt(2+x); dy=0.5_wp/y
      case(5)
         y=sin(2*x)*cos(x); dy=2*cos(2*x)*cos(x)-sin(2*x)*sin(x)
      case(6)
         y=atan(x); dy=1/(1+x*x)
      case(7)
         y=tan(0.5_wp*x); dy=0.5_wp/cos(0.5_wp*x)**2
      case(8)
         y=(2+x)**1.5_wp; dy=1.5_wp*sqrt(2+x)
      case(9)
         y=2.0_wp**x; dy=log(2.0_wp)*y
      case(10)
         y=(2+x)**(1+0.25_wp*x)
         dy=y*(0.25_wp*log(2+x)+(1+0.25_wp*x)/(2+x))
      case(11)
         y=asin(x/2); dy=0.5_wp/sqrt(1-(x/2)**2)
      case(12)
         y=acos(x/2); dy=-0.5_wp/sqrt(1-(x/2)**2)
      end select
   end subroutine reference
end module derivative_reference_functions
program checked_forwarddiff
   use derivative_reference_functions
   use ieee_arithmetic, only: ieee_is_finite
   implicit none
   real(wp) :: x,y,dy,expected,slope,worst=0,error
   integer :: i,calls=0
   do degree=0,8
      do i=-32,32
         x=real(i,wp)/16
         if (degree==0) then
            expected=3; slope=0
         else
            expected=x**degree; slope=degree*x**(degree-1)
         end if
         call derivative(monomial,x,y,dy)
         call check()
      end do
   end do
   do expression=1,12
      do i=-48,48
         x=real(i,wp)/32
         call reference(x,expected,slope)
         call derivative(composite,x,y,dy)
         call check()
      end do
   end do
   print '(a,i0)', 'Scalar derivative calls: ',calls
   print '(a,i0)', 'Analytic value/slope references: ',2*calls
   print '(a,es12.4)', 'Maximum normalized error: ',worst
   print '(a)', 'PASS forwarddiff-analytic-reference'
contains
   subroutine check()
      if (.not.all(ieee_is_finite([y,dy]))) error stop 'nonfinite AD output'
      error=max(abs(y-expected)/(1+abs(expected)),abs(dy-slope)/(1+abs(slope)))
      worst=max(worst,error)
      if (error>2e-12_wp) error stop 'analytic derivative mismatch'
      calls=calls+1
   end subroutine check
end program checked_forwarddiff
