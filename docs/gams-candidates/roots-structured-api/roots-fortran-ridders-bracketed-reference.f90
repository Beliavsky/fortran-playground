! Independent MIT consumer; see licenses/roots-structured-ten-drivers-MIT.txt.
program main
   use iso_fortran_env,only:wp=>real64
   use ieee_arithmetic,only:ieee_is_finite
   use root_module,only:root_scalar
   implicit none
   real(wp)::r,x,fx,lo,hi
   integer::i,k,status,count
   logical::fallback
   count=0
   do k=1,5
      do i=-8,8
         r=real(i,wp)/4
         lo=r-0.75_wp;hi=r+1.25_wp
         call root_scalar('ridders',fun,lo,hi,x,fx,status, &
            ftol=1.e-13_wp,atol=1.e-12_wp,rtol=1.e-12_wp,maxiter=500, &
            bisect_on_failure=.false.,bisect_used=fallback)
         if(status/=0.or.fallback) error stop 'Root solver status or fallback'
         if(x<lo.or.x>hi) error stop 'Root outside bracket'
         call check(x,r);call check(fx,0._wp);call check(fun(x),0._wp)
         count=count+1
      end do
   end do
   print '(a,i0)', 'Manufactured roots, five nonlinear families: ',count
   print '(a)', 'PASS roots-fortran-ridders-bracketed-reference'
contains
   function fun(t) result(y)
      real(wp),intent(in)::t
      real(wp)::y,z
      z=t-r
      select case(k)
      case(1)
         y=z*(1+z*z)
      case(2)
         y=exp(z)-1
      case(3)
         y=sin(z)
      case(4)
         y=log(1+z)
      case(5)
         y=z/(2+z*z)
      end select
   end function
   subroutine check(a,b)
      real(wp),intent(in)::a,b
      if(.not.ieee_is_finite(a)) error stop 'Nonfinite result'
      if(abs(a-b)>2.e-9_wp*max(1._wp,abs(b))) then
         print *, 'actual, reference:',a,b
         error stop 'Independent reference'
      end if
   end subroutine
end program
