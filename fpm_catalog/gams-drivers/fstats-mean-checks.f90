! Adapted author descriptive-statistics API patterns; shared deterministic checks.
! MIT License
! 
! Copyright (c) 2022-2026 Jason Christopherson
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
program checked_descriptive_statistics
   use iso_fortran_env, only: wp=>real64
   use ieee_arithmetic, only: ieee_is_finite
   use fstats, only: mean
   implicit none
   real(wp), parameter :: base(5)=[1._wp,2._wp,3._wp,4._wp,5._wp]
   logical, parameter :: mask(5)=[.true.,.false.,.true.,.false.,.true.]
   real(wp) :: samples(5),answer,expected,error,max_error
   integer :: problem
   max_error=0._wp
   do problem=1,4
      select case(problem)
      case(1)
         samples=base
      case(2)
         samples=1.e6_wp+2._wp*base
      case(3)
         samples=7.25_wp
      case(4)
         samples=-3._wp*base
      end select
      select case(problem)
      case(1)
         expected=3._wp
      case(2)
         expected=1.e6_wp+6._wp
      case(3)
         expected=7.25_wp
      case(4)
         expected=-9._wp
      end select
      answer=mean(samples)
      if (.not.ieee_is_finite(answer)) error stop 'nonfinite mean'
      error=abs(answer-expected)/max(1._wp,abs(expected))
      if (error>64._wp*epsilon(1._wp)) error stop 'independent known mean'
      max_error=max(max_error,error)
      print '(a,i0)', 'Mean case: ',problem
      print '(a,es22.14)', 'Computed mean: ',answer
      print '(a,es12.4)', 'Scaled absolute mean error: ',error
   end do
   answer=mean(pack(base,mask))
   if (.not.ieee_is_finite(answer).or.abs(answer-3._wp)>1.e-12_wp) error stop 'packed subset mean'
   print '(a,es22.14)', 'Mean of subset [1,3,5]: ',answer
   print '(a,es12.4)', 'Maximum scaled mean error: ',max_error
   print '(a)', 'PASS fstats-mean-checks'
end program
