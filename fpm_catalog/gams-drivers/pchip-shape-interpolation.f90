! Adapted author interpolation API patterns; shared deterministic data and checks.
! PCHIP: Piecewise Cubic Hermite Interpolation Package
! https://github.com/jacobwilliams/PCHIP
! 
! Copyright (c) 2019-2024, Jacob Williams
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
! *********************************************************************************
! 
! This library contains code from SLATEC a public domain work of the U.S. Government.
! The SLATEC notice follows:
! 
! The SLATEC Common Mathematical Library is issued by the following
! 
!         Air Force Weapons Laboratory, Albuquerque
!         Lawrence Livermore National Laboratory, Livermore
!         Los Alamos National Laboratory, Los Alamos
!         National Institute of Standards and Technology, Washington
!         National Energy Research Supercomputer Center, Livermore
!         Oak Ridge National Laboratory, Oak Ridge
!         Sandia National Laboratories, Albuquerque
!         Sandia National Laboratories, Livermore
! 
! All questions concerning the distribution of the library should be
! directed to the NATIONAL ENERGY SOFTWARE CENTER, 9700 Cass Ave.,
! Argonne, Illinois  60439, and not to the authors of the subprograms.
! 
!                  * * * * * Notice * * * * *
! 
! This material was prepared as an account of work sponsored by the
! United States Government.  Neither the United States, nor the
! Department of Energy, nor the Department of Defense, nor any of
! their employees, nor any of their contractors, subcontractors, or
! their employees, makes any warranty, expressed or implied, or
! assumes any legal liability or responsibility for the accuracy,
! completeness, or usefulness of any information, apparatus, product,
! or process disclosed, or represents that its use would not infringe
! upon privately owned rights.
program checked_interpolation
   use iso_fortran_env, only: wp=>real64
   use ieee_arithmetic, only: ieee_is_finite
   use pchip_module, only: dpchim,dpchfe
   implicit none
   integer, parameter :: n=6
   real(wp), parameter :: x(n)=[0._wp,0.25_wp,0.5_wp,1._wp,2._wp,3._wp]
   real(wp) :: f(n),query,answer,previous,reference,theta
   real(wp) :: node_error,affine_error,linear_difference,bound_violation,decrease
   integer :: problem,i,j,evaluations
   real(wp) :: slopes(1,n),tabulated(1,n),queries(1),answers(1)
   integer :: status
   logical :: skip
   do problem=1,2
      if (problem==1) then
         f=2._wp*x-1._wp
         print '(a)', 'Case: affine data f(x)=2*x-1'
      else
         f=[0._wp,0.01_wp,0.02_wp,0.9_wp,0.95_wp,1._wp]
         print '(a)', 'Case: steep monotone data'
      end if
      tabulated(1,:)=f
      call dpchim(n,x,tabulated,slopes,1,status)
      if (status/=0) error stop 'interpolator initialization'
      evaluations=0; node_error=0._wp; affine_error=0._wp; linear_difference=0._wp
      bound_violation=0._wp; decrease=0._wp
      do i=1,n
         call evaluate(x(i),answer)
         node_error=max(node_error,abs(answer-f(i)))
      end do
      if (node_error>1.e-12_wp) error stop 'interpolation at original nodes'
      previous=f(1)
      print '(a)', '  Interval midpoint       Interpolated value'
      do i=1,n-1
         do j=0,20
            theta=real(j,wp)/20._wp
            query=x(i)+theta*(x(i+1)-x(i))
            call evaluate(query,answer)
            reference=(1._wp-theta)*f(i)+theta*f(i+1)
            linear_difference=max(linear_difference,abs(answer-reference))
            bound_violation=max(bound_violation,f(i)-answer,answer-f(i+1))
            decrease=max(decrease,previous-answer)
            if (problem==1) affine_error=max(affine_error,abs(answer-(2._wp*query-1._wp)))
            if (j==10) print '(2f24.14)', query,answer
            previous=answer
         end do
      end do
      if (bound_violation>1.e-12_wp.or.decrease>1.e-12_wp) error stop 'sampled monotonicity or overshoot'
      if (affine_error>1.e-12_wp) error stop 'affine preservation'
      print '(a,es12.4)', 'Maximum node error: ',node_error
      if (problem==1) print '(a,es12.4)', 'Maximum affine reproduction error: ',affine_error
      print '(a,es12.4)', 'Maximum difference from piecewise linear: ',linear_difference
      print '(a,es12.4)', 'Maximum sampled local bound violation: ',bound_violation
      print '(a,es12.4)', 'Maximum sampled decrease: ',decrease
      print '(a,i0)', 'Evaluator calls: ',evaluations
   end do
   print '(a)', 'PASS pchip-shape-interpolation'
contains
   subroutine evaluate(t,value)
      real(wp), intent(in) :: t
      real(wp), intent(out) :: value
      evaluations=evaluations+1
      skip=.false.
      queries(1)=t
      call dpchfe(n,x,tabulated,slopes,1,skip,1,queries,answers,status)
      value=answers(1)
      if (status/=0.or..not.ieee_is_finite(value)) error stop 'interpolation evaluation'
   end subroutine
end program
