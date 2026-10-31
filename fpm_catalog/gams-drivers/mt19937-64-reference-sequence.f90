! Adapted author API usage; deterministic sequence/replay checks.
! BSD 3-Clause License
! 
! Copyright (c) 2022, Jacob Williams
! All rights reserved.
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
! 
! -------------------------------------------------------------------------------
! 
!    Translated from C-program for MT19937-64 (2004/9/29 version)
!    originally coded by Takuji Nishimura and Makoto Matsumoto
!    http://www.math.sci.hiroshima-u.ac.jp/~m-mat/me%mt/emt64.html
! 
! -------------------------------------------------------------------------------
! 
!    Fortran translation by Rémi Piatek
!    The University of Copenhagen
!    Department of Economics
!    email: {first}.{last}@econ.ku.dk
! 
! -------------------------------------------------------------------------------
!    A C-program for MT19937-64 (2004/9/29 version).
!    Coded by Takuji Nishimura and Makoto Matsumoto.
! 
!    Copyright (C) 2004, Makoto Matsumoto and Takuji Nishimura,
!    All rights reserved.
! 
!    Redistribution and use in source and binary forms, with or without
!    modification, are permitted provided that the following conditions
!    are met:
! 
!      1. Redistributions of source code must retain the above copyright
!         notice, this list of conditions and the following disclaimer.
! 
!      2. Redistributions in binary form must reproduce the above copyright
!         notice, this list of conditions and the following disclaimer in the
!         documentation and/or other materials provided with the distribution.
! 
!      3. The names of its contributors may not be used to endorse or promote
!         products derived from this software without specific prior written
!         permission.
! 
!    THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
!    "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
!    LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
!    A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER
!    OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
!    EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
!    PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
!    PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
!    LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
!    NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
!    SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
program checked_random_sequence
   use iso_fortran_env, only: wp=>real64,int64
   use ieee_arithmetic, only: ieee_is_finite
   use mt19937_64, only: mt19937
   implicit none
   integer, parameter :: count=1000
   integer, parameter :: positions(15)=[ &
      1,2,3,4,5,6,7,8,9,10, &
      312,313,624,625,1000]
   integer(int64), parameter :: references(15)=[ &
      int(z'C96D191CF6F6AEA6',int64), &
      int(z'401F7AC78BC80F1C',int64), &
      int(z'B5EE8CB6ABE457F8',int64), &
      int(z'F258D22D4DB91392',int64), &
      int(z'04EEF2B4B5D860CC',int64), &
      int(z'67A7AABE10D172D6',int64), &
      int(z'40565D50E72B4021',int64), &
      int(z'05D07B7D1E8DE386',int64), &
      int(z'8548DEA130821ACC',int64), &
      int(z'583C502C832E0A3A',int64), &
      int(z'13038D24C91C1BB8',int64), &
      int(z'5E0B18C0F57393B1',int64), &
      int(z'D7C295AFC52A1C17',int64), &
      int(z'AB1BF7646B530A67',int64), &
      int(z'8D7573457A93F389',int64)]
   type(mt19937) :: raw_generator,uniform_generator
   integer(int64) :: bits
   real(wp) :: values(count),again,expected
   integer :: i,j
   call raw_generator%initialize(5489_int64)
   call uniform_generator%initialize(5489_int64)
   j=1
   do i=1,count
      bits=raw_generator%genrand64_int64()
      values(i)=uniform_generator%genrand64_real2()
      expected=real(shiftr(bits,11),wp)*2._wp**(-53)
      if (.not.ieee_is_finite(values(i)).or.values(i)<0._wp.or.values(i)>=1._wp) error stop 'uniform range'
      if (values(i)/=expected) error stop 'integer-to-uniform conversion'
      if (i==positions(j)) then
         if (bits/=references(j)) error stop 'independent MT19937-64 integer reference'
         print '(a,i4,a,z16.16)', 'Reference output ',i,': ',bits
         if (j<size(positions)) j=j+1
      end if
   end do
   call uniform_generator%initialize(5489_int64)
   do i=1,count
      again=uniform_generator%genrand64_real2()
      if (again/=values(i)) error stop 'MT seeded replay'
   end do
   print '(a,i0)', 'Exact uniform conversion/replay checks: ',count
   print '(a,5f16.12)', 'First five uniform draws: ',values(:5)
   print '(a)', 'PASS mt19937-64-reference-sequence'
end program
