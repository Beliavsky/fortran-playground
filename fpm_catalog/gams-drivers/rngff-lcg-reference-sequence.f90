! Adapted author API usage; deterministic sequence/replay checks.
! MIT License
! 
! Copyright (c) 2023 Archaeologic, Inc., Brad Richardson
! This software was developed for the U.S. Nuclear Regulatory Commission (US NRC) under contract # 31310020D0006:
! "Technical Assistance in Support of NRC Nuclear Regulatory Research for Materials, Waste, and Reactor Programs"
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
   use iso_fortran_env, only: wp=>real64,real32,int32,int64
   use ieee_arithmetic, only: ieee_is_finite
   use rngff, only: linear_congruential_t
   implicit none
   integer, parameter :: count=1000
   integer(int64), parameter :: modulus(2)=[2147483563_int64,2147483399_int64]
   integer(int64), parameter :: multiplier(2)=[40014_int64,40692_int64]
   integer(int64) :: state(2),z
   type(linear_congruential_t) :: generator,replay
   real(wp) :: value,again,expected,first(5)
   integer :: i
   state=[12345_int64,67890_int64]
   generator=linear_congruential_t(12345_int32,67890_int32)
   replay=linear_congruential_t(12345_int32,67890_int32)
   do i=1,count
      ! Direct int64 modular multiplication is independent of the package's int32 Schrage update.
      state=modulo(multiplier*state,modulus)
      z=state(1)-state(2)
      if (z<1_int64) z=z+modulus(1)-1_int64
      ! The real64 overload widens a real32 value; reproduce that specified rounding step.
      expected=real(real(real(z,wp)/real(modulus(1),wp),real32),wp)
      if (expected>=1._wp) expected=0._wp
      call generator%next(value)
      call replay%next(again)
      if (.not.ieee_is_finite(value).or.value<0._wp.or.value>=1._wp) error stop 'LCG uniform range'
      if (any(int(generator%seeds(),int64)/=state)) error stop 'independent LCG state reference'
      if (value/=expected) error stop 'independent LCG real32-rounded output'
      if (value/=again) error stop 'LCG seeded replay'
      if (i<=5) first(i)=value
   end do
   print '(a,i0)', 'Exact modular-state/output/replay checks: ',count
   print '(a,2i14)', 'Final two-seed state: ',state
   print '(a,5f16.12)', 'First five uniform draws: ',first
   print '(a)', 'The real64 overload returns widened real32 draws.'
   print '(a)', 'PASS rngff-lcg-reference-sequence'
end program
