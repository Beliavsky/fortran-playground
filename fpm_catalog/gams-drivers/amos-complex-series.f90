! Original C10 API driver. MIT: licenses/special-function-drivers-MIT.txt.
! Known pinned failure at z=2-0.75i retained under docs/gams-candidates/amosf90.
program main
   use iso_fortran_env, only: dp=>real64
   use ieee_arithmetic, only: ieee_is_finite
   use amos, only: f90_zbesj,f90_zbesi,f90_zbesk
   implicit none
   complex(dp),parameter :: arguments(*)=[cmplx(.5_dp,.25_dp,dp),cmplx(1._dp,.5_dp,dp),cmplx(2._dp,.75_dp,dp)]
   real(dp),parameter :: orders(*)=[.3_dp,.5_dp,1.25_dp],pi=acos(-1._dp)
   complex(dp) :: jvalues(2),ivalues(2),kvalue(1),z,reference
   real(dp) :: nu,maximum_error
   integer :: i,j,m,nz,status,checks
   maximum_error=0
   checks=0
   do i=1,size(arguments)
      z=arguments(i)
      do j=1,size(orders)
         nu=orders(j)
         call f90_zbesj(z,nu,1,2,jvalues,nz,status)
         if(status/=0 .or. nz/=0) error stop 'AMOS J status/underflow'
         call f90_zbesi(z,nu,1,2,ivalues,nz,status)
         if(status/=0 .or. nz/=0) error stop 'AMOS I status/underflow'
         do m=1,2
            call check(jvalues(m),series(z,nu+m-1,-1))
            call check(ivalues(m),series(z,nu+m-1,1))
         end do
      end do
      call f90_zbesk(z,.5_dp,1,1,kvalue,nz,status)
      if(status/=0 .or. nz/=0) error stop 'AMOS K status/underflow'
      reference=sqrt(pi/(2*z))*exp(-z)
      call check(kvalue(1),reference)
      print '(a,2f10.4,a,2f20.12)', 'z = ',real(z),aimag(z), '; K_0.5(z) = ',real(kvalue(1)),aimag(kvalue(1))
   end do
   if(checks/=39) error stop 'case count'
   print '(a,i0)', 'Independent complex Bessel values checked: ',checks
   print '(a,es12.4)', 'Maximum scaled error: ',maximum_error
   print '(a)', 'PASS amos-complex-series'
contains
   subroutine check(value,expected)
      complex(dp),intent(in) :: value,expected
      real(dp) :: error
      if(.not.all(ieee_is_finite([real(value),aimag(value),real(expected),aimag(expected)]))) &
         error stop 'nonfinite complex reference'
      error=abs(value-expected)/max(1._dp,abs(expected))
      maximum_error=max(maximum_error,error)
      if(error>2.e-12_dp) then
         print '(a,2f16.8,a,f12.6,a,i0)', 'At z=',real(z),aimag(z),'; starting order=',nu,'; sequence index=',m
         print '(a,2es24.16)', 'Actual:   ',real(value),aimag(value)
         print '(a,2es24.16)', 'Reference:',real(expected),aimag(expected)
         print '(a,es24.16)', 'Scaled error:',error
         error stop 'complex Bessel reference'
      end if
      checks=checks+1
   end subroutine
   function series(x,order,sign_factor) result(value)
      complex(dp),intent(in) :: x
      real(dp),intent(in) :: order
      integer,intent(in) :: sign_factor
      complex(dp) :: value,term,total
      integer :: k
      logical :: converged
      term=cmplx(1._dp,0._dp,dp)
      total=term
      converged=.false.
      do k=1,100
         term=term*(sign_factor*x*x/4)/(k*(order+k))
         total=total+term
         if(abs(term)<=epsilon(1._dp)*max(1._dp,abs(total))) then
            converged=.true.
            exit
         end if
      end do
      if(.not.converged) error stop 'reference series did not converge'
      value=(x/2)**order*total/gamma(order+1)
   end function
end program
