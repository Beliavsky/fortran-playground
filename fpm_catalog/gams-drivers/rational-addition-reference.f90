! Original GAMS A2 API driver. MIT: licenses/arithmetic-drivers-MIT.txt.
program main
   use iso_fortran_env, only: int64
   use rational_number, only: rationalnumber_t, ratNumInit, ratNumAdd, ratNumToStr, &
      ratNumGetNumerator, ratNumGetDenominator
   implicit none
   type(rationalnumber_t) :: left, right, answer
   integer :: p, q, r, s, mode, calls, num, den, divisor, common
   integer(int64) :: expected_num, expected_den
   calls = 0
   do p = -4, 4
      do q = 1, 6
         do r = -4, 4
            do s = 1, 6
               left = ratNumInit(p, q)
               right = ratNumInit(r, s)
               expected_num = int(p,int64)*s + int(r,int64)*q
               expected_den = int(q,int64)*s
               do mode = 0, 1
                  answer = ratNumAdd(left, right, simplify=(mode == 1))
                  num = ratNumGetNumerator(answer)
                  den = ratNumGetDenominator(answer)
                  if (den <= 0) error stop 'denominator sign'
                  if (int(num,int64)*expected_den /= expected_num*den) error stop 'exact rational sum'
                  if (mode == 1 .and. expected_num > 0) then
                     common = 1
                     do divisor = 1, int(min(expected_num,expected_den))
                        if (modulo(expected_num,int(divisor,int64)) == 0 .and. &
                            modulo(expected_den,int(divisor,int64)) == 0) common = divisor
                     end do
                     if (num /= expected_num/common .or. den /= expected_den/common) &
                        error stop 'positive sum reduction'
                  end if
                  calls = calls + 1
               end do
            end do
         end do
      end do
   end do
   answer = ratNumAdd(ratNumInit(1,3), ratNumInit(1,6), simplify=.true.)
   print '(a)', '1/3 + 1/6 = '//ratNumToStr(answer)
   answer = ratNumAdd(ratNumInit(-1,3), ratNumInit(-1,6), simplify=.true.)
   print '(a)', '-1/3 - 1/6 = '//ratNumToStr(answer)//' (same value as -1/2)'
   print '(a,i0)', 'Exact additions checked with simplify off/on: ', calls
   if (calls /= 5832) error stop 'case count'
   print '(a)', 'Pinned simplifier does not reduce negative/zero numerators; value checks allow this.'
   print '(a)', 'PASS rational-addition-reference'
end program
