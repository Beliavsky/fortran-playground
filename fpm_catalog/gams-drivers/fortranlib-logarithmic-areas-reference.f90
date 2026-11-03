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
      integral_linlog,integral_loglin,integral_loglog, &
      cumulative_integral_linlog,cumulative_integral_loglin,cumulative_integral_loglog
   implicit none
   real(wp),parameter::x(5)=[0.5_wp,1._wp,2._wp,4._wp,8._wp]
   real(wp),parameter::limits(11)=[0.25_wp,0.5_wp,0.75_wp,1._wp,1.5_wp, &
      2._wp,3._wp,4._wp,6._wp,8._wp,9._wp]
   real(wp)::y(5),c(5),p,value,full,lo,hi,expected
   integer::mode,k,n,a,b,i,cases
   cases=0
   do mode=1,3
      n=3;if(mode==3)n=5
      do k=1,n
         p=parameter(mode,k);y=field(x,mode,p)
         select case(mode)
         case(1)
            full=integral_linlog(x,y);c=cumulative_integral_linlog(x,y)
         case(2)
            full=integral_loglin(x,y);c=cumulative_integral_loglin(x,y)
         case(3)
            full=integral_loglog(x,y);c=cumulative_integral_loglog(x,y)
         end select
         call check(full,primitive(x(5),mode,p)-primitive(x(1),mode,p))
         do i=1,5
            call check(c(i),primitive(x(i),mode,p)-primitive(x(1),mode,p))
         end do
         do a=1,size(limits)
            do b=a,size(limits)
               lo=max(limits(a),x(1));hi=min(limits(b),x(5));expected=0
               if(hi>lo) expected=primitive(hi,mode,p)-primitive(lo,mode,p)
               select case(mode)
               case(1)
                  value=integral_linlog(x,y,limits(a),limits(b))
               case(2)
                  value=integral_loglin(x,y,limits(a),limits(b))
               case(3)
                  value=integral_loglog(x,y,limits(a),limits(b))
               end select
               call check(value,expected);cases=cases+1
            end do
         end do
      end do
   end do
   print '(a,i0)', 'Logarithmic subset areas checked: ',cases
   print '(a)', '11 full integrals and 55 cumulative-prefix values independently checked.'
   print '(a)', 'PASS fortranlib-logarithmic-areas-reference'
end program
