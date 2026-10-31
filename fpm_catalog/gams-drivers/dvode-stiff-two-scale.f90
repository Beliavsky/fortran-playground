! Author API patterns adapted on 2026-10-30 to an exact autonomous two-scale stiff system.
! Modern Fortran Edition of the DVODE ODE Solver
! https://github.com/jacobwilliams/dvode
! 
! Copyright (c) 2016-2023, Jacob Williams
! All rights reserved.
! 
! Redistribution and use in source and binary forms, with or without modification,
! are permitted provided that the following conditions are met:
! 
! * Redistributions of source code must retain the above copyright notice, this
!   list of conditions and the following disclaimer.
! 
! * Redistributions in binary form must reproduce the above copyright notice, this
!   list of conditions and the following disclaimer in the documentation and/or
!   other materials provided with the distribution.
! 
! * The names of its contributors may not be used to endorse or promote products
!   derived from this software without specific prior written permission.
! 
! THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
! ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
! WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
! DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
! ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
! (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
! LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
! ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
! (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
! SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
! 
! ## VODE Software Release Statement
! 
! ### NOTICE
! 
! This work was produced at the University of California, Lawrence Livermore National Laboratory (UC LLNL) under
! contract no. W-7405-ENG-48 (Contract 48) between the U.S. Department of Energy (DOE) and The Regents of the University
! of California (University) for the operation of UC LLNL. The rights of the Federal Government are reserved under
! Contract 48 subject to the restrictions agreed upon by the DOE and University as allowed under DOE Acquisition Letter
! 97-1.
! 
! The VODE package has been declared to be in the Public Domain.
! 
! ### DISCLAIMER
! 
! This work was prepared as an account of work sponsored by an agency of the United States Government. Neither the
! United States Government nor the University of California nor any of their employees, makes any warranty, express or
! implied, or assumes any liability or responsibility for the accuracy, completeness, or usefulness of any information,
! apparatus, product, or process disclosed, or represents that its use would not infringe privately-owned rights.
! Reference herein to any specific commercial products, process, or service by trade name, trademark, manufacturer or
! otherwise does not necessarily constitute or imply its endorsement, recommendation, or favoring by the United States
! Government or the University of California. The views and opinions of authors expressed herein do not necessarily
! state or reflect those of the United States Government or the University of California, and shall not be used for
! advertising or product endorsement purposes.
module stiff_equations
   use dvode_module, only: dvode_t
   use dvode_kinds_module, only: wp=>dvode_wp
   implicit none
contains
   subroutine rates(me,n,time,y,dy)
      class(dvode_t), intent(inout) :: me
      integer :: n
      real(wp) :: time,y(n),dy(n)
      dy(1)=-1000._wp*y(1)+999._wp*y(2)
      dy(2)=-y(2)
   end subroutine
end module
program checked_stiff_system
   use stiff_equations
   use ieee_arithmetic, only: ieee_is_finite
   implicit none
   real(wp), parameter :: targets(4)=[0.001_wp,0.01_wp,0.1_wp,1._wp]
   real(wp) :: y(2),time,exact(2),scaled_error,fast_error
   integer :: i
   type(dvode_t) :: solver
   real(wp) :: work(100)
   integer :: iwork(40),state
   call solver%initialize(f=rates)
   time=0._wp;y=[2._wp,1._wp];work=0._wp;iwork=0;state=1
   do i=1,size(targets)
      ! MF=22: BDF with internally approximated dense Jacobian. State=2 continues integration.
      call solver%solve(2,y,time,targets(i),1,[1.e-8_wp],[1.e-10_wp],1,state,0,work,100,iwork,40,22)
      if (state/=2) error stop 'DVODE did not report successful integration'
      if (.not.all(ieee_is_finite(y)).or..not.ieee_is_finite(time)) error stop 'nonfinite integration result'
      if (abs(time-targets(i))>1.e-12_wp) error stop 'target time mismatch'
      exact=[exp(-time)+exp(-1000._wp*time),exp(-time)]
      scaled_error=maxval(abs(y-exact)/max(1._wp,abs(exact)))
      fast_error=abs((y(1)-y(2))-exp(-1000._wp*time))
      if (scaled_error>2.e-6_wp.or.fast_error>4.e-6_wp) error stop 'exact stiff solution mismatch'
      print '(a,f8.4,a,2f15.10)', 't=',time,' state=',y
      print '(a,2es13.4)', 'Scaled state error / fast-mode error:',scaled_error,fast_error
      print '(a,i0,a,i0)', 'Total steps=',iwork(11),' RHS evaluations=',iwork(12)
   end do
   print '(a)', 'PASS dvode-stiff-two-scale'
end program
