! Independent MIT consumer; see licenses/transforms-structures-ten-drivers-MIT.txt.
program main
   use iso_fortran_env, only: wp=>real64
   use pchip_module, only: dpchsp,dpchfd
   use ieee_arithmetic, only: ieee_is_finite
   implicit none
   real(wp),parameter :: nodes(6)=[-1._wp,-0.5_wp,0.25_wp,1._wp,1.75_wp,3._wp]
   real(wp) :: values(1,6),slopes(1,6),workspace(2,6),vc(2),queries(25),f(25),d(25),x
   integer :: pattern,mode,i,status,ic(2),cases
   logical :: skip
   cases=0
   do pattern=1,3
      values(1,:)=(nodes-real(pattern,wp)/4)**3-2*nodes+real(pattern,wp)/8
      do mode=0,2
         ic=mode; vc=0
         if(mode==1) vc=3*([nodes(1),nodes(6)]-real(pattern,wp)/4)**2-2
         if(mode==2) vc=6*([nodes(1),nodes(6)]-real(pattern,wp)/4)
         call dpchsp(ic,vc,6,nodes,values,slopes,1,workspace,12,status)
         if(status/=0) error stop 'Cubic spline boundary-condition setup'
         do i=1,25
            queries(i)=nodes(1)+real(i-1,wp)*(nodes(6)-nodes(1))/24
         end do
         skip=.false.
         call dpchfd(6,nodes,values,slopes,1,skip,25,queries,f,d,status)
         if(status/=0) error stop 'Cubic spline value/derivative evaluation'
         do i=1,25
            x=queries(i)
            call check(f(i),(x-real(pattern,wp)/4)**3-2*x+real(pattern,wp)/8)
            call check(d(i),3*(x-real(pattern,wp)/4)**2-2)
            cases=cases+1
         end do
      end do
   end do
   print '(a,i0)', 'Cubic spline values/derivatives: not-a-knot, first/second derivative boundaries: ',cases
   print '(a)', 'PASS pchip-cubic-boundaries-reference'
contains
   subroutine check(actual,expected)
      real(wp),intent(in) :: actual,expected
      if(.not.ieee_is_finite(actual)) error stop 'Nonfinite result'
      if(abs(actual-expected)>2.e-9_wp*max(1._wp,abs(expected))) error stop 'Independent reference'
   end subroutine
end program
