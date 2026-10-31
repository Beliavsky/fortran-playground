! Original C14 API driver. MIT: licenses/special-function-drivers-MIT.txt.
program main
   use carlson_elliptic_module, only: wp=>carlson_elliptic_module_wp, drf
   use ieee_arithmetic, only: ieee_is_finite
   implicit none
   real(wp), parameter :: triples(3,3)=reshape([0.25_wp,1._wp,4._wp, &
      1._wp,2._wp,4._wp, 2._wp,3._wp,5._wp],[3,3])
   real(wp), parameter :: moduli(*)=[0._wp,0.25_wp,0.75_wp,0.95_wp]
   real(wp), parameter :: diagonal(*)=[0.25_wp,1._wp,4._wp]
   real(wp) :: x,y,z,k,actual,reference,coarse,fine,max_error,pi,u,h,total
   integer :: i,j,status
   pi=acos(-1._wp)
   max_error=0
   do i=1,size(diagonal)
      x=diagonal(i)
      actual=drf(x,x,x,status)
      call check(actual,1/sqrt(x),status)
   end do
   do i=1,3
      x=triples(1,i); y=triples(2,i); z=triples(3,i)
      actual=drf(x,y,z,status)
      if(status/=0) error stop 'RF status'
      coarse=rf_integral(x,y,z,2048)
      fine=rf_integral(x,y,z,4096)
      call check(coarse,fine,0)
      call check(actual,fine,0)
      reference=drf(y,z,x,status)
      call check(reference,actual,status)
      reference=drf(4*x,4*y,4*z,status)
      call check(reference,actual/2,status)
   end do
   print '(a)', 'k             Complete elliptic K(k)'
   do i=1,size(moduli)
      k=moduli(i)
      actual=drf(0._wp,1-k*k,1._wp,status)
      if(status/=0) error stop 'elliptic K status'
      h=pi/(2*4096)
      total=1+1/sqrt(1-k*k)
      do j=1,4095
         u=j*h
         total=total+merge(4._wp,2._wp,mod(j,2)==1)/sqrt(1-k*k*sin(u)**2)
      end do
      reference=total*h/3
      call check(actual,reference,0)
      print '(f6.2,f26.16)',k,actual
   end do
   print '(a,es12.4)', 'Maximum scaled reference/identity error: ',max_error
   print '(a)', 'PASS carlson-rf-reference'
contains
   subroutine check(value,expected,code)
      real(wp), intent(in) :: value,expected
      integer,intent(in) :: code
      real(wp) :: error
      if(code/=0) error stop 'RF status'
      if(.not.ieee_is_finite(value) .or. .not.ieee_is_finite(expected)) error stop 'nonfinite RF'
      error=abs(value-expected)/max(1._wp,abs(expected))
      max_error=max(max_error,error)
      if(error>2.e-11_wp) error stop 'RF reference check'
   end subroutine
   function rf_integral(a,b,c,n) result(value)
      real(wp),intent(in) :: a,b,c
      integer,intent(in) :: n
      real(wp) :: value,t,term,step
      integer :: j
      ! t=1/sqrt(1+u) transforms the defining RF integral to a smooth finite interval.
      step=1._wp/n
      value=1+1/sqrt(a*b*c)
      do j=1,n-1
         t=j*step
         term=1/sqrt((1+(a-1)*t*t)*(1+(b-1)*t*t)*(1+(c-1)*t*t))
         value=value+merge(4._wp,2._wp,mod(j,2)==1)*term
      end do
      value=value*step/3
   end function
end program
