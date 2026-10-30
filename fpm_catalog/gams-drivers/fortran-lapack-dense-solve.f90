! Additional shared problem data source notice:
! MIT License
! 
! Copyright (c) 2019-2021 stdlib contributors
! 
! Permission is hereby granted, free of charge, to any person obtaining a copy
! of this software and associated documentation files (the "Software"), to deal
! in the Software without restriction, including without limitation the rights
! to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
! copies of the Software, and to permit persons to whom the Software is
! furnished to do so, subject to the following conditions:
! 
! The above copyright notice and this permission notice shall be included in all
! copies or substantial portions of the Software.
! 
! THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
! IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
! FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
! AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
! LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
! OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
! SOFTWARE.
! Adapted author API examples; shared deterministic problems and independent checks.
! BSD 3-Clause License
! 
! Copyright (c) 2024, Federico Perini
! 
! Redistribution and use in source and binary forms, with or without
! modification, are permitted provided that the following conditions are met:
! 
! 1. Redistributions of source code must retain the above copyright notice, this
!    list of conditions and the following disclaimer.
! 
! 2. Redistributions in binary form must reproduce the above copyright notice,
!    this list of conditions and the following disclaimer in the documentation
!    and/or other materials provided with the distribution.
! 
! 3. Neither the name of the copyright holder nor the names of its
!    contributors may be used to endorse or promote products derived from
!    this software without specific prior written permission.
! 
! THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
! AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
! IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
! DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
! FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
! DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
! SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
! CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
! OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
! OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
program checked_linear_algebra
   use iso_fortran_env, only: wp=>real64
   use ieee_arithmetic, only: ieee_is_finite
   use linear_algebra, only: solve
   use la_state_type, only: la_state
   use la_constants, only: ilp
   implicit none
   type(la_state) :: state
   real(wp) :: a(3,3),original(3,3),b(3),rhs(3),x(3),expected(3),residual(3)
   real(wp) :: solution_error,scaled_residual,denominator
   integer :: problem
   do problem=1,2
      if (problem==1) then
         ! From stdlib's example_solve1, expressed in double precision.
         a=transpose(reshape([4._wp,3._wp,2._wp,-2._wp,2._wp,3._wp,3._wp,-5._wp,2._wp],[3,3]))
         b=[25._wp,-10._wp,-4._wp]
         expected=[5._wp,3._wp,-2._wp]
      else
         ! From fortran-lapack's test_dsolve.
         a=transpose(reshape([1._wp,3._wp,3._wp,1._wp,3._wp,4._wp,1._wp,4._wp,3._wp],[3,3]))
         b=[1._wp,4._wp,-1._wp]
         expected=[-2._wp,-2._wp,3._wp]
      end if
      original=a; rhs=b
      x=solve(a,b,err=state)
      if (state%error()) then
         print *, state%print()
         error stop 'dense solver status'
      end if
      if (.not.all(ieee_is_finite(x))) error stop 'nonfinite solution'
      residual=matmul(original,x)-rhs
      solution_error=maxval(abs(x-expected))
      denominator=maxval(sum(abs(original),dim=2))*maxval(abs(x))+maxval(abs(rhs))
      scaled_residual=maxval(abs(residual))/denominator
      if (solution_error>1.e-10_wp.or.scaled_residual>1.e-12_wp) error stop 'independent solve accuracy'
      print '(a,i0)', 'Dense nonsymmetric case: ', problem
      print '(a,3f18.12)', 'Solution: ', x
      print '(a,es12.4)', 'Maximum solution error: ', solution_error
      print '(a,es12.4)', 'Scaled infinity-norm residual: ', scaled_residual
   end do
   print '(a)', 'PASS fortran-lapack-dense-solve'
end program
