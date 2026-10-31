! GAMS B: direct use of the calculator's number-theory routines, without its UI.
! Original API driver; upstream MIT notice retained in licenses/rpn-calculator-MIT.txt.
program main
   use rat, only: gcd, lcm
   implicit none
   integer :: a, b, divisor, multiple, expected_gcd, expected_lcm, checked_lcm
   checked_lcm = 0
   do a = 0, 64
      do b = 0, 64
         ! Independent reference: enumerate every possible common divisor.
         expected_gcd = 0
         do divisor = 1, max(a, b)
            if (modulo(a, divisor) == 0 .and. modulo(b, divisor) == 0) expected_gcd = divisor
         end do
         if (gcd(a, b) /= expected_gcd) then
            print '(a,2(1x,i0))', 'GCD mismatch:', a, b
            error stop 'greatest common divisor'
         end if
         ! The pinned LCM implementation divides by gcd(a,b): (0,0) is outside its domain.
         if (a == 0 .and. b == 0) cycle
         expected_lcm = 0
         if (a > 0 .and. b > 0) then
            ! Search positive multiples; do not use gcd or the package LCM formula.
            do multiple = max(a, b), a*b, max(a, b)
               if (modulo(multiple, a) == 0 .and. modulo(multiple, b) == 0) then
                  expected_lcm = multiple
                  exit
               end if
            end do
         end if
         if (lcm(a, b) /= expected_lcm) then
            print '(a,2(1x,i0))', 'LCM mismatch:', a, b
            error stop 'least common multiple'
         end if
         checked_lcm = checked_lcm + 1
      end do
   end do
   print '(a,i0)', 'gcd(48,18) = ', gcd(48,18)
   print '(a,i0)', 'lcm(48,18) = ', lcm(48,18)
   print '(a)', 'Checked 4225 GCD and 4224 LCM cases for operands 0 through 64.'
   if (checked_lcm /= 4224) error stop 'case count'
   print '(a)', 'Zero operands checked; lcm(0,0), negative signs and overflow are outside this example.'
   print '(a)', 'PASS rpn-gcd-lcm-reference'
end program
