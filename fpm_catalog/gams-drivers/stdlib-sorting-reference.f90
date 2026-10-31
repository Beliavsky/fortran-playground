! Author sorting API patterns adapted on 2026-10-30 to exact deterministic sorting checks.
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
program checked_sorting
   use iso_fortran_env, only: wp=>real64,int32
   use stdlib_sorting, only: sort
   use ieee_arithmetic, only: ieee_is_finite
   implicit none
   integer(int32), parameter :: input(8)=[5,-3,0,-3,2,1,5,-1],expected(8)=[-3,-3,-1,0,1,2,5,5]
   real(wp), parameter :: real_input(7)=[2.5_wp,-1.25_wp,0._wp,0.5_wp,-1.25_wp,2._wp,-3._wp]
   real(wp), parameter :: real_expected(7)=[-3._wp,-1.25_wp,-1.25_wp,0._wp,0.5_wp,2._wp,2.5_wp]
   integer(int32) :: values(8),large(64),large_expected(64),original(64),empty(0),single(1)
   real(wp) :: real_values(7)
   integer :: i,value,position,copies
   values=input
   call sort(values)
   if (any(values/=expected)) error stop 'ascending integer sort mismatch'
   print '(a,8i5)', 'Ascending integers:',values
   call sort(values)
   if (any(values/=expected)) error stop 'sort is not idempotent'
   values=input
   call sort(values,reverse=.true.)
   if (any(values/=expected(8:1:-1))) error stop 'descending integer sort mismatch'
   print '(a,8i5)', 'Descending integers:',values
   real_values=real_input
   call sort(real_values)
   if (.not.all(ieee_is_finite(real_values))) error stop 'nonfinite sorted values'
   if (any(real_values/=real_expected)) error stop 'ascending real sort mismatch'
   print '(a,7f9.3)', 'Ascending real values:',real_values
   real_values=real_input
   call sort(real_values,reverse=.true.)
   if (any(real_values/=real_expected(7:1:-1))) error stop 'descending real sort mismatch'
   do i=1,size(large)
      original(i)=modulo(37*i,17)-8
   end do
   ! Build an exact sorted reference from counts in the known integer range, not another sort.
   position=0
   do value=-8,8
      copies=count(original==value)
      large_expected(position+1:position+copies)=value
      position=position+copies
   end do
   if (position/=size(large)) error stop 'histogram reference size'
   large=original
   call sort(large)
   if (any(large/=large_expected)) error stop 'histogram-reference sort mismatch'
   print '(a,i0,a)', 'Sorted ',size(large),' repeated integers against a histogram reference.'
   call sort(empty)
   single=[42]
   call sort(single)
   if (single(1)/=42) error stop 'singleton sort mismatch'
   print '(a)', 'Empty and singleton arrays checked.'
   print '(a)', 'PASS stdlib-sorting-reference'
end program
