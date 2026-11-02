! Independent MIT consumer; see licenses/grids-ten-drivers-MIT.txt.
program main
   use iso_fortran_env, only: real64, int64
   use ieee_arithmetic, only: ieee_is_finite
   use stdlib_math, only: gcd
   implicit none

   integer :: a,b,d,expected,count
   integer(int64) :: value
   count=0
   do a=-40,40
      do b=-40,40
         expected=0
         do d=1,40
            if(mod(a,d)==0.and.mod(b,d)==0) expected=d
         end do
         if(a==0.and.b==0) expected=0
         value=gcd(int(a,int64),int(b,int64))
         if(value/=expected) error stop 'Exhaustive divisor reference'
         count=count+1
      end do
   end do
   if(gcd(600000000000_int64,900000000000_int64)/=300000000000_int64) error stop 'Large common divisor'
   if(gcd(-600000000000_int64,900000000000_int64)/=300000000000_int64) error stop 'Large signed divisor'
   if(gcd(1000000007_int64,1000000009_int64)/=1_int64) error stop 'Large coprime pair'
   if(gcd(0_int64,-900000000000_int64)/=900000000000_int64) error stop 'Large zero operand'
   print '(a,i0,a)', 'Exhaustive signed GCD pairs: ',count,'; large exact cases: 4'
   print '(a)', 'PASS stdlib-gcd-reference'
end program
