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
   use lib_array,only:interp2d
   implicit none
   real(wp),parameter::x(4)=[-1._wp,0._wp,0.75_wp,2._wp],y(3)=[-2._wp,-0.5_wp,1._wp]
   real(wp)::data(4,3),qx,qy,a,b,c,d,value,expected
   integer::variant,i,j,cases
   cases=0
   do variant=1,3
      a=real(variant,wp)/4;b=-0.5_wp;c=0.75_wp;d=real(variant-2,wp)/2
      do i=1,4
         do j=1,3
            data(i,j)=a+b*x(i)+c*y(j)+d*x(i)*y(j)
         end do
      end do
      do i=0,24
         do j=0,24
            qx=-1+real(i,wp)/8;qy=-2+real(j,wp)/8
            expected=a+b*qx+c*qy+d*qx*qy
            value=interp2d(x,y,data,qx,qy)
            call check(value,expected);cases=cases+1
         end do
      end do
      call check(interp2d(x,y,data,-1.25_wp,0._wp,.false.,-123._wp),-123._wp)
      call check(interp2d(x,y,data,2.25_wp,0._wp,.false.,-123._wp),-123._wp)
      call check(interp2d(x,y,data,0._wp,-2.25_wp,.false.,-123._wp),-123._wp)
      call check(interp2d(x,y,data,0._wp,1.25_wp,.false.,-123._wp),-123._wp)
   end do
   print '(a,i0)', 'Independent bilinear values including boundaries: ',cases
   print '(a)', '12 explicit outside-fill values checked.'
   print '(a)', 'PASS fortranlib-bilinear-surfaces-reference'
end program
