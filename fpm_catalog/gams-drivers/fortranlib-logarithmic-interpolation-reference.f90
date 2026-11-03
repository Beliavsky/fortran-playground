! Independent MIT consumer; see licenses/fortranlib-tables-drivers-MIT.txt.
module reference_model
   use iso_fortran_env,only:wp=>real64
   use ieee_arithmetic,only:ieee_is_finite
   implicit none
contains
   elemental function parameter(mode,k) result(p)
      integer,intent(in)::mode,k
      real(wp)::p
      real(wp),parameter::powers(5)=[-2._wp,-1._wp,0._wp,0.5_wp,2._wp]
      select case(mode)
      case(0)
         p=real(k-2,wp)
      case(1)
         p=real(k-2,wp)/4
      case(2)
         p=real(k-2,wp)/2
      case(3)
         p=powers(k)
      end select
   end function
   elemental function field(x,mode,p) result(y)
      real(wp),intent(in)::x,p
      integer,intent(in)::mode
      real(wp)::y
      select case(mode)
      case(0)
         y=2+p*x
      case(1)
         y=3*exp(p*x)
      case(2)
         y=2+p*log(x)
      case(3)
         y=3*x**p
      end select
   end function
   elemental function primitive(x,mode,p) result(y)
      real(wp),intent(in)::x,p
      integer,intent(in)::mode
      real(wp)::y
      select case(mode)
      case(0)
         y=2*x+p*x*x/2
      case(1)
         if(p==0) then
            y=3*x
         else
            y=3*exp(p*x)/p
         end if
      case(2)
         y=2*x+p*(x*log(x)-x)
      case(3)
         if(p==-1) then
            y=3*log(x)
         else
            y=3*x**(p+1)/(p+1)
         end if
      end select
   end function
   subroutine check(actual,expected)
      real(wp),intent(in)::actual,expected
      if(.not.ieee_is_finite(actual)) error stop 'Nonfinite result'
      if(abs(actual-expected)>2.e-11_wp*max(1._wp,abs(expected))) then
         print *, 'Actual, expected:',actual,expected
         error stop 'Independent analytic reference'
      end if
   end subroutine
end module
program main
   use reference_model
   use lib_array,only: &
      interp1d_linlog,interp1d_loglin,interp1d_loglog
   implicit none
   real(wp),parameter::x(5)=[0.5_wp,1._wp,2._wp,4._wp,8._wp]
   real(wp)::y(5),q(65),values(65),p,expected,scalar
   integer::mode,k,n,i,cases
   q(:61)=[(0.5_wp+real(i-1,wp)/8,i=1,61)];q(62:)=[0.25_wp,0.375_wp,9._wp,10._wp]
   cases=0
   do mode=1,3
      n=3;if(mode==3)n=5
      do k=1,n
         p=parameter(mode,k);y=field(x,mode,p)
         select case(mode)
         case(1)
            values=interp1d_linlog(x,y,q,bounds_error=.false.,fill_value=-123._wp)
         case(2)
            values=interp1d_loglin(x,y,q,bounds_error=.false.,fill_value=-123._wp)
         case(3)
            values=interp1d_loglog(x,y,q,bounds_error=.false.,fill_value=-123._wp)
         end select
         do i=1,size(q)
            expected=-123
            if(q(i)>=x(1).and.q(i)<=x(5)) expected=field(q(i),mode,p)
            select case(mode)
            case(1)
               scalar=interp1d_linlog(x,y,q(i),bounds_error=.false.,fill_value=-123._wp)
            case(2)
               scalar=interp1d_loglin(x,y,q(i),bounds_error=.false.,fill_value=-123._wp)
            case(3)
               scalar=interp1d_loglog(x,y,q(i),bounds_error=.false.,fill_value=-123._wp)
            end select
            call check(values(i),expected);call check(scalar,expected);cases=cases+1
         end do
      end do
   end do
   print '(a,i0)', 'Logarithmic scalar/vector query pairs checked: ',cases
   print '(a)', 'PASS fortranlib-logarithmic-interpolation-reference'
end program
