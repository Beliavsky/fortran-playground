! Adapted author descriptive-statistics API patterns; shared deterministic checks.
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
program checked_descriptive_statistics
   use iso_fortran_env, only: wp=>real64
   use ieee_arithmetic, only: ieee_is_finite
   use stdlib_stats, only: var
   implicit none
   real(wp), parameter :: base(5)=[1._wp,2._wp,3._wp,4._wp,5._wp]
   logical, parameter :: mask(5)=[.true.,.false.,.true.,.false.,.true.]
   real(wp) :: samples(5),answer,expected,error,max_error
   integer :: problem
   real(wp) :: matrix(5,2),columns(2)
   real(wp) :: population,expected_population
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
         expected=2.5_wp
      case(2)
         expected=10._wp
      case(3)
         expected=0._wp
      case(4)
         expected=22.5_wp
      end select
      answer=var(samples,corrected=.true.)
      population=var(samples,corrected=.false.)
      if (.not.ieee_is_finite(answer).or..not.ieee_is_finite(population)) error stop 'nonfinite variance'
      if (answer<0._wp.or.population<0._wp) error stop 'negative variance'
      expected_population=expected*4._wp/5._wp
      error=max(abs(answer-expected)/max(1._wp,expected), &
         abs(population-expected_population)/max(1._wp,expected_population))
      if (error>1.e-12_wp) error stop 'independent sample/population variance'
      max_error=max(max_error,error)
      print '(a,i0)', 'Variance case: ',problem
      print '(a,f18.12)', 'Sample variance (N-1 denominator): ',answer
      print '(a,f18.12)', 'Population variance (N denominator): ',population
      print '(a,es12.4)', 'Maximum scaled variance error: ',error
   end do
   answer=var(pack(base,mask),corrected=.true.)
   if (.not.ieee_is_finite(answer).or.abs(answer-4._wp)>1.e-12_wp) error stop 'packed subset variance'
   print '(a,f18.12)', 'Sample variance of subset [1,3,5]: ',answer
   answer=var(base,mask=mask,corrected=.true.)
   population=var(base,mask=mask,corrected=.false.)
   if (.not.ieee_is_finite(answer).or..not.ieee_is_finite(population)) error stop 'nonfinite masked variance'
   if (abs(answer-4._wp)>1.e-12_wp.or.abs(population-8._wp/3._wp)>1.e-12_wp) &
      error stop 'native masked variance'
   matrix(:,1)=base; matrix(:,2)=2._wp*base
   columns=var(matrix,dim=1,corrected=.true.)
   if (.not.all(ieee_is_finite(columns)).or.maxval(abs(columns-[2.5_wp,10._wp]))>1.e-12_wp) &
      error stop 'column variances'
   print '(a,2f18.12)', 'Column sample variances [base,2*base]: ',columns
   print '(a,es12.4)', 'Maximum scaled variance error: ',max_error
   print '(a)', 'PASS stdlib-sample-variance-checks'
end program
