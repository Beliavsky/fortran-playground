! Independent MIT consumer; see licenses/transforms-structures-ten-drivers-MIT.txt.
program main
   use iso_fortran_env, only: wp=>real64
   use pchip_module, only: dpchia,dpchid
   use ieee_arithmetic, only: ieee_is_finite
   implicit none
   real(wp),parameter :: nodes(6)=[-1.0_wp,-0.5_wp,0.25_wp,1.0_wp,1.75_wp,3.0_wp]
   real(wp),parameter :: values(1,6)=reshape([2.0_wp,-0.25_wp,0.5_wp,0.75_wp,-1.0_wp,1.5_wp],[1,6])
   real(wp),parameter :: slopes(1,6)=reshape([0.5_wp,-0.75_wp,1.0_wp,0.0_wp,1.25_wp,-0.5_wp],[1,6])
   real(wp) :: a,b,actual,expected,h,left,right,middle,offset,total,t,value
   integer :: i,j,k,sign,ier,cases
   logical :: skip
   cases=0
   do i=0,8
      a=nodes(1)+real(i,wp)*(nodes(6)-nodes(1))/8
      do j=0,8
         b=nodes(1)+real(j,wp)*(nodes(6)-nodes(1))/8
         expected=reference_integral(a,b); skip=.false.; ier=0
         actual=dpchia(6,nodes,values,slopes,1,skip,a,b,ier)
         if(ier/=0) error stop 'Hermite arbitrary-endpoint integral status'
         call check(actual,expected); cases=cases+1
      end do
   end do
   do i=1,6
      do j=1,6
         skip=.false.; ier=0
         actual=dpchid(6,nodes,values,slopes,1,skip,i,j,ier)
         if(ier/=0) error stop 'Hermite node-index integral status'
         call check(actual,reference_integral(nodes(i),nodes(j))); cases=cases+1
      end do
   end do
   print '(a,i0)', 'Piecewise cubic integrals with arbitrary/reversed/node-index bounds: ',cases
   print '(a)', 'PASS pchip-hermite-integrals-reference'
contains
   function reference_integral(a,b) result(result)
      real(wp),intent(in) :: a,b
      real(wp) :: result,left,right,h,middle,offset,t,v
      integer :: i,side
      result=0
      do i=1,5
         left=max(min(a,b),nodes(i)); right=min(max(a,b),nodes(i+1))
         if(left>=right) cycle
         h=nodes(i+1)-nodes(i); middle=(left+right)/2; offset=(right-left)/(2*sqrt(3._wp))
         do side=-1,1,2
            t=(middle+side*offset-nodes(i))/h
            v=(2*t**3-3*t*t+1)*values(1,i)+(-2*t**3+3*t*t)*values(1,i+1) &
               +h*((t**3-2*t*t+t)*slopes(1,i)+(t**3-t*t)*slopes(1,i+1))
            result=result+(right-left)*v/2
         end do
      end do
      if(b<a) result=-result
   end function
   subroutine check(actual,expected)
      real(wp),intent(in) :: actual,expected
      if(.not.ieee_is_finite(actual)) error stop 'Nonfinite result'
      if(abs(actual-expected)>2.e-9_wp*max(1._wp,abs(expected))) error stop 'Independent reference'
   end subroutine
end program
