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
      rebin,rebin_linlog,rebin_loglin,rebin_loglog
   implicit none
   real(wp),parameter::x(5)=[0.5_wp,1._wp,2._wp,4._wp,8._wp]
   real(wp),parameter::centers(6)=[0.5_wp,1._wp,1.5_wp,2.5_wp,4._wp,8._wp]
   real(wp)::y(5),means(6),left,right,p,expected,mass
   integer::mode,k,n,i,cases
   cases=0
   do mode=0,3
      n=3;if(mode==3)n=5
      do k=1,n
         p=parameter(mode,k);y=field(x,mode,p)
         select case(mode)
         case(0)
            call rebin(x,y,centers,means)
         case(1)
            call rebin_linlog(x,y,centers,means)
         case(2)
            call rebin_loglin(x,y,centers,means)
         case(3)
            call rebin_loglog(x,y,centers,means)
         end select
         mass=0
         do i=1,6
            left=centers(1);right=centers(6)
            if(mode<=1) then
               if(i>1)left=(centers(i-1)+centers(i))/2
               if(i<6)right=(centers(i)+centers(i+1))/2
            else
               if(i>1)left=sqrt(centers(i-1)*centers(i))
               if(i<6)right=sqrt(centers(i)*centers(i+1))
            end if
            expected=(primitive(right,mode,p)-primitive(left,mode,p))/(right-left)
            call check(means(i),expected);mass=mass+means(i)*(right-left);cases=cases+1
         end do
         call check(mass,primitive(x(5),mode,p)-primitive(x(1),mode,p))
      end do
   end do
   print '(a,i0)', 'Independent conservative cell means checked: ',cases
   print '(a)', '14 total-area conservation identities checked.'
   print '(a)', 'PASS fortranlib-conservative-rebinning-reference'
end program
