! Author API patterns adapted on 2026-10-30 to an exact autonomous two-scale stiff system.
! NOTICE
! 
! This work was produced at the University of California, Lawrence Livermore
! National Laboratory (UC LLNL) under contract no. W-7405-ENG-48 (Contract
! 48) between the U.S. Department of Energy (DOE) and The Regents of the
! University of California (University) for the operation of UC LLNL. The
! rights of the Federal Government are reserved under Contract 48 subject
! to the restrictions agreed upon by the DOE and University as allowed
! under DOE Acquisition Letter 97-1.
! 
! The ODEPACK package has been declared to be in the Public Domain.
! 
! DISCLAIMER
! 
! This work was prepared as an account of work sponsored by an agency of
! the United States Government. Neither the United States Government nor the
! University of California nor any of their employees, makes any warranty,
! express or implied, or assumes any liability or responsibility for the
! accuracy, completeness, or usefulness of any information, apparatus,
! product, or process disclosed, or represents that its use would not
! infringe privately-owned rights. Reference herein to any specific
! commercial products, process, or service by trade name, trademark,
! manufacturer or otherwise does not necessarily constitute or imply
! its endorsement, recommendation, or favoring by the United States
! Government or the University of California. The views and opinions of
! authors expressed herein do not necessarily state or reflect those of
! the United States Government or the University of California, and shall
! not be used for advertising or product endorsement purposes.
module stiff_equations
   use odepack_mod, only: wp=>dp,lsoda_class
   implicit none
contains
   subroutine rates(me,n,time,y,dy,status)
      class(lsoda_class), intent(inout) :: me
      integer, intent(in) :: n
      real(wp), intent(in) :: time,y(n)
      real(wp), intent(out) :: dy(n)
      integer, intent(out) :: status
      dy(1)=-1000._wp*y(1)+999._wp*y(2)
      dy(2)=-y(2)
      status=0
   end subroutine
end module
program checked_stiff_system
   use stiff_equations
   use ieee_arithmetic, only: ieee_is_finite
   implicit none
   real(wp), parameter :: targets(4)=[0.001_wp,0.01_wp,0.1_wp,1._wp]
   real(wp) :: y(2),time,exact(2),scaled_error,fast_error
   integer :: i
   type(lsoda_class) :: solver
   integer :: state,method,steps,evaluations
   logical :: saw_bdf
   call solver%initialize(rates,2,istate=state,mxstep=5000)
   if (state<0) error stop 'LSODA initialization failed'
   time=0._wp;y=[2._wp,1._wp];state=1;saw_bdf=.false.
   do i=1,size(targets)
      call solver%integrate(y,time,targets(i),1.e-8_wp,[1.e-10_wp],1,state)
      if (state/=2) error stop 'LSODA did not report successful integration'
      if (.not.all(ieee_is_finite(y)).or..not.ieee_is_finite(time)) error stop 'nonfinite integration result'
      if (abs(time-targets(i))>1.e-12_wp) error stop 'target time mismatch'
      exact=[exp(-time)+exp(-1000._wp*time),exp(-time)]
      scaled_error=maxval(abs(y-exact)/max(1._wp,abs(exact)))
      fast_error=abs((y(1)-y(2))-exp(-1000._wp*time))
      if (scaled_error>2.e-6_wp.or.fast_error>4.e-6_wp) error stop 'exact stiff solution mismatch'
      print '(a,f8.4,a,2f15.10)', 't=',time,' state=',y
      print '(a,2es13.4)', 'Scaled state error / fast-mode error:',scaled_error,fast_error
      call solver%info(meth=method,nst=steps,nfe=evaluations)
      if (method/=1.and.method/=2) error stop 'invalid LSODA method indicator'
      saw_bdf=saw_bdf.or.method==2
      print '(a,i0,a,i0,a,i0)', 'Current method (1=Adams, 2=BDF)=',method, &
         ' total steps=',steps,' RHS evaluations=',evaluations
   end do
   if (.not.saw_bdf) error stop 'BDF mode was not observed for the stiff problem'
   print '(a)', 'PASS lsoda-stiff-two-scale'
end program
