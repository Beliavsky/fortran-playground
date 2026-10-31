! Original C19 API driver. MIT: licenses/special-function-drivers-MIT.txt.
program main
   use iso_fortran_env, only: int64
   use specfun_module, only: bernob, wp=>specfun_wp
   use ieee_arithmetic, only: ieee_is_finite
   implicit none
   integer,parameter :: indices(*)=[0,1,2,4,6,8,10,12], sizes(*)=[3,10,20]
   integer,parameter :: numerators(*)=[1,-1,1,-1,1,-1,5,-691]
   integer,parameter :: denominators(*)=[1,2,6,30,42,30,66,2730]
   real(wp) :: values(0:12),coefficients(0:12),expected,actual,maximum_error,error
   integer(int64) :: direct,choose
   integer :: i,j,p,n,m,checks
   call bernob(12,values)
   maximum_error=0
   coefficients=0
   do i=1,size(indices)
      j=indices(i)
      expected=real(numerators(i),wp)/denominators(i)
      if(.not.ieee_is_finite(values(j))) error stop 'nonfinite Bernoulli number'
      error=abs(values(j)-expected)/max(1._wp,abs(expected))
      maximum_error=max(maximum_error,error)
      if(error>3.e-12_wp) error stop 'Bernoulli rational reference'
      coefficients(j)=values(j)
      print '(a,i0,a,f23.15)', 'B(',j,') = ',values(j)
   end do
   ! bernob does not assign odd output positions >1 at this pin. Do not read them.
   ! Their mathematical zeros are supplied locally for the independent power-sum application.
   checks=0
   do i=1,size(sizes)
      n=sizes(i)
      do p=1,8
         direct=0
         do m=0,n-1
            direct=direct+int(m,int64)**p
         end do
         actual=0
         choose=1
         do j=0,p
            actual=actual+real(choose,wp)*coefficients(j)*real(n,wp)**(p+1-j)
            choose=choose*(p+1-j)/(j+1)
         end do
         actual=actual/(p+1)
         expected=real(direct,wp)
         error=abs(actual-expected)/max(1._wp,abs(expected))
         maximum_error=max(maximum_error,error)
         if(.not.ieee_is_finite(actual) .or. error>3.e-12_wp) error stop 'integer power sum'
         checks=checks+1
      end do
   end do
   print '(a,i0)', 'Independent integer power sums checked: ',checks
   print '(a,es12.4)', 'Maximum scaled error: ',maximum_error
   print '(a)', 'Odd outputs above B1 are unassigned at this pin and are not read.'
   print '(a)', 'PASS bernoulli-power-sums'
end program
