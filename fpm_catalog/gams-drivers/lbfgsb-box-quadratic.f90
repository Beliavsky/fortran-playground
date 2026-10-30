! Adapted reverse-communication pattern from author driver1; retained license.
! 3-clause license ("New BSD License" or "Modified BSD License")
! New BSD License
! Author	Regents of the University of California
! Publisher	Public Domain
! Published	July 22, 1999[8]
! DFSG compatible	Yes[7]
! FSF approved	Yes[1]
! OSI approved	Yes[3]
! GPL compatible	Yes[1]
! Copyleft	No[1]
! Copyfree	Yes
! Linking from code with a different license	Yes
! 
! The advertising clause was removed from the license text in the official BSD on July 22, 1999 by William Hoskins, Director of 
! the Office of Technology Licensing for UC Berkeley.[8] Other BSD distributions removed the clause, but many similar clauses 
! remain in BSD-derived code from other sources, and unrelated code using a derived license.
! 
! While the original license is sometimes referred to as "BSD-old", the resulting 3-clause version is sometimes referred to by 
! "BSD-new." Other names include "New BSD", "revised BSD", "BSD-3", or "3-clause BSD". This version has been vetted as 
! an Open source license by the OSI as the "The BSD License".[3] The Free Software Foundation, which refers to the license 
! as the "Modified BSD License", states that it is compatible with the GNU GPL. The FSF encourages users to be specific 
! when referring to the license by name (i.e. not simply referring to it as "a BSD license" or "BSD-style") to avoid confusion with 
! the original BSD license.[1]
! 
! This version allows unlimited redistribution for any purpose as long as its copyright notices and the license's disclaimers of 
! warranty are maintained. The license also contains a clause restricting use of the names of contributors for endorsement of a 
! derived work without specific permission.
! 
! Copyright (c) <year>, <copyright holder>
! All rights reserved.
! 
! Redistribution and use in source and binary forms, with or without
! modification, are permitted provided that the following conditions are met:
!     * Redistributions of source code must retain the above copyright
!       notice, this list of conditions and the following disclaimer.
!     * Redistributions in binary form must reproduce the above copyright
!       notice, this list of conditions and the following disclaimer in the
!       documentation and/or other materials provided with the distribution.
!     * Neither the name of the <organization> nor the
!       names of its contributors may be used to endorse or promote products
!       derived from this software without specific prior written permission.
! 
! THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
! ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
! WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
! DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> BE LIABLE FOR ANY
! DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
! (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
! LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
! ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
! (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
! SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
! 
! 
! References
! 
! 1. ^ a b c d e "Various Licenses and Comments about Them - GNU Project - Free Software Foundation (FSF): Modified BSD license". 
!      Free Software Foundation. Retrieved 02 October 2010.
! 2. ^ a b c d e "Various Licenses and Comments about Them - GNU Project - Free Software Foundation (FSF): FreeBSD license". 
!      Free Software Foundation. Retrieved 02 October 2010.
! 3. ^ a b c d e f "Open Source Initiative OSI - The BSD License:Licensing". Open Source Initiative. Retrieved 06 December 2009.
! 4. ^ a b c d "Various Licenses and Comments about Them - GNU Project - Free Software Foundation (FSF): Original BSD license". 
!      Free Software Foundation. Retrieved 02 October 2010.
! 5. ^ The year given is the year 4.3BSD-Tahoe was released. Whether this is the first use of the license is not known.
! 6. ^ The year given is the year 4.3BSD-Reno was released. Whether this is the first use of the license is not known.
! 7. ^ a b "Debian -- License information". Debian. Retrieved 18 February 2010.
! 8. ^ a b c "To All Licensees, Distributors of Any Version of BSD". University of California, Berkeley. 1999-07-22. Retrieved 
!      2006-11-15.
! 9. ^ Richard Stallman. "The BSD License Problem". Free Software Foundation. Retrieved 2006-11-15.
! 10. ^ "The FreeBSD Copyright". The FreeBSD Project. Retrieved 6 December 2009.
! 11. ^ "NetBSD Licensing and Redistribution". The NetBSD Foundation. Retrieved 06 December 2009.
module box_model
   use iso_fortran_env, only: wp=>real64
   implicit none
   real(wp), parameter :: lower(2)=[0._wp,0._wp],upper(2)=[1._wp,2._wp],target(2)=[2._wp,-1._wp]
   integer :: objective_calls=0,gradient_calls=0
contains
   pure function value(x) result(f)
      real(wp), intent(in) :: x(:)
      real(wp) :: f
      f=sum((x-target)**2)
   end function
   pure function derivative(x) result(g)
      real(wp), intent(in) :: x(:)
      real(wp) :: g(size(x))
      g=2._wp*(x-target)
   end function
   subroutine check_gradient()
      real(wp) :: x(2),plus(2),minus(2),fd(2)
      real(wp), parameter :: h=1.e-6_wp
      integer :: j
      x=[0.25_wp,1._wp]
      do j=1,2
         plus=x; minus=x; plus(j)=plus(j)+h; minus(j)=minus(j)-h
         fd(j)=(value(plus)-value(minus))/(2._wp*h)
      end do
      if (maxval(abs(fd-derivative(x)))>1.e-7_wp) error stop 'analytic objective gradient'
   end subroutine
end module
program checked_box_minimum
   use box_model
   use ieee_arithmetic, only: ieee_is_finite
   use lbfgsb_module, only: setulb
   implicit none
   real(wp) :: x(2),reported,independent,feasibility,projected
   integer, parameter :: n=2,mem=5
   real(wp) :: g(n),wa(2*mem*n+5*n+11*mem*mem+8*mem),dsave(29)
   integer :: nbd(n),iwa(3*n),isave(44),iteration
   logical :: lsave(4)
   character(60) :: task,csave
   call check_gradient()
   x=[0.25_wp,1._wp]; nbd=2; task='START'
   do iteration=1,1000
      call setulb(n,mem,x,lower,upper,nbd,reported,g,1.e7_wp,1.e-10_wp, &
         wa,iwa,task,-1,csave,lsave,isave,dsave)
      if (task(1:2)=='FG') then
         reported=value(x); g=derivative(x)
         objective_calls=objective_calls+1; gradient_calls=gradient_calls+1
      else if (task(1:5)/='NEW_X') then
         exit
      end if
   end do
   if (task(1:4)/='CONV') error stop 'L-BFGS-B did not converge'
   if (.not.all(ieee_is_finite(x)).or..not.ieee_is_finite(reported)) error stop 'nonfinite optimum'
   independent=value(x)
   feasibility=max(0._wp,maxval(lower-x),maxval(x-upper))
   projected=maxval(abs(x-min(upper,max(lower,x-derivative(x)))))
   if (feasibility>1.e-10_wp.or.projected>1.e-8_wp) error stop 'box feasibility/stationarity'
   if (maxval(abs(x-[1._wp,0._wp]))>1.e-8_wp.or.abs(independent-2._wp)>1.e-8_wp) &
      error stop 'known box optimum'
   if (abs(reported-independent)>1.e-10_wp) error stop 'reported objective disagreement'
   if (objective_calls<=0.or.gradient_calls<=0) error stop 'missing analytic evaluations'
   print '(a,2f18.12)', 'Computed minimizer: ',x
   print '(a,f18.12)', 'Independent objective (expected 2): ',independent
   print '(a,es12.4)', 'Maximum bound violation: ',feasibility
   print '(a,es12.4)', 'Projected gradient residual: ',projected
   print '(a,i0)', 'Objective evaluations: ',objective_calls
   print '(a,i0)', 'Gradient evaluations: ',gradient_calls
   print '(a,a)', 'Solver termination: ',trim(task)
   print '(a)', 'PASS lbfgsb-box-quadratic'
end program
