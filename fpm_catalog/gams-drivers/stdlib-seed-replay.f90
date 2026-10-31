! Adapted author API usage; deterministic sequence/replay checks.
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
program checked_random_sequence
   use iso_fortran_env, only: int64
   use stdlib_random, only: seed_distribution=>random_seed,dist_rand
   implicit none
   integer, parameter :: count=1024
   integer(int64), parameter :: seed=1234567_int64
   integer(int64) :: values(count),other(count),again,get_first,get_repeat,get_other
   integer :: i
   call seed_distribution(seed,get_first)
   do i=1,count
      values(i)=dist_rand(0_int64) ! The argument selects the result kind.
   end do
   call seed_distribution(seed,get_repeat)
   if (get_first/=get_repeat) error stop 'inconsistent seed get output'
   do i=1,count
      again=dist_rand(0_int64)
      if (again/=values(i)) error stop 'stdlib integer seeded replay'
   end do
   call seed_distribution(seed+1_int64,get_other)
   do i=1,count
      other(i)=dist_rand(0_int64)
   end do
   if (all(other==values)) error stop 'selected seed change left sequence unchanged'
   print '(a,i0)', 'Exact integer replay checks: ',count
   print '(a,z16.16)', 'Opaque get output for the selected seed: ',get_first
   print '(a)', 'First five integer draws (hexadecimal bit patterns):'
   do i=1,5
      print '(i3,1x,z16.16)',i,values(i)
   end do
   print '(a)', 'The second selected seed changed the sequence.'
   print '(a)', 'This seeds stdlib distributions; intrinsic RANDOM_NUMBER has its own seed API.'
   print '(a)', 'PASS stdlib-seed-replay'
end program
