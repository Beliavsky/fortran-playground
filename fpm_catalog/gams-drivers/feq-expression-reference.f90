! Independent API consumer; see licenses/expressions-sky-drivers-MIT.txt.
program checked_feq_expressions
   use iso_fortran_env, only: real64
   use ieee_arithmetic, only: ieee_is_finite
   use FEQParse, only: EquationParser
   implicit none
   integer, parameter :: n=343
   character(len=80), parameter :: expressions(12)=[character(len=80) :: &
      'f = x + 2*y - z', 'f = (x + 2*y)^2 + z', 'f = x*y + y*z + z*x', &
      'f = (x-y)/(2+z^2)', 'f = exp(-(x^2+y^2+z^2))', 'f = sin(x)+cos(y)-tan(z/4)', &
      'f = sqrt(2+x^2)+log(2+y^2)', 'f = abs(x-y)+abs(z)', 'f = (x^2)^2+(y^2)^2+(z^2)^2', &
      'f = pi*(x^2+y^2)+z', 'f = 2^(x/2)', 'f = exp(sin(x))+sqrt(1+y^2)/(2+z^2)']
   real(real64) :: points(n,3),reversed(n,3),saved(n,3),expected(n),actual(n),other(n),value,worst=0
   integer :: i,j,k,l,expression,checks=0
   l=0
   do i=-3,3
      do j=-3,3
         do k=-3,3
            l=l+1; points(l,:)=[real(i,real64),real(j,real64),real(k,real64)]/2
         end do
      end do
   end do
   reversed=points(:,3:1:-1); saved=points
   do expression=1,12
      block
         type(EquationParser) :: parser,reverse_parser
         parser=EquationParser(trim(expressions(expression)),['x','y','z'])
         reverse_parser=EquationParser(trim(expressions(expression)),['z','y','x'])
         do i=1,n
            expected(i)=reference(expression,points(i,1),points(i,2),points(i,3))
            value=parser%evaluate(points(i,:))
            call compare(value,expected(i))
         end do
         actual=parser%evaluate(points)
         other=reverse_parser%evaluate(reversed)
         do i=n,1,-1
            call compare(actual(i),expected(i))
            call compare(other(i),expected(i))
            value=reverse_parser%evaluate(reversed(i,:))
            call compare(value,expected(i))
         end do
         if (any(points/=saved).or.any(reversed/=saved(:,3:1:-1))) error stop 'expression inputs changed'
      end block
   end do
   print '(a,i0)', 'Parsed expressions: ',size(expressions)
   print '(a,i0)', 'Scalar/batch formula references: ',checks
   print '(a,es12.4)', 'Maximum normalized evaluation error: ',worst
   print '(a)', 'PASS feq-expression-reference'
contains
   function reference(expression,x,y,z) result(f)
      integer, intent(in) :: expression
      real(real64), intent(in) :: x,y,z
      real(real64) :: f
      select case(expression)
      case(1)
         f=x+2*y-z
      case(2)
         f=(x+2*y)**2+z
      case(3)
         f=x*y+y*z+z*x
      case(4)
         f=(x-y)/(2+z*z)
      case(5)
         f=exp(-x*x-y*y-z*z)
      case(6)
         f=sin(x)+cos(y)-tan(z/4)
      case(7)
         f=sqrt(2+x*x)+log(2+y*y)
      case(8)
         f=abs(x-y)+abs(z)
      case(9)
         f=x*x*x*x+y*y*y*y+z*z*z*z
      case(10)
         f=acos(-1.0_real64)*(x*x+y*y)+z
      case(11)
         f=exp(log(2.0_real64)*x/2)
      case(12)
         f=exp(sin(x))+sqrt(1+y*y)/(2+z*z)
      end select
   end function reference
   subroutine compare(got,expected)
      real(real64), intent(in) :: got,expected
      real(real64) :: error
      if (.not.ieee_is_finite(got)) error stop 'nonfinite expression value'
      error=abs(got-expected)/(1+abs(expected)); worst=max(worst,error)
      if (error>2e-12_real64) error stop 'direct expression reference mismatch'
      checks=checks+1
   end subroutine compare
end program checked_feq_expressions
