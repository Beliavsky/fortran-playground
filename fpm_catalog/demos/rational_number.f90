program main
   use rational_number
   implicit none
   type(rationalnumber_t) :: total
   total = ratNumAdd(ratNumInit(1,3), ratNumInit(1,6), simplify=.true.)
   if (ratNumGetNumerator(total) /= 1 .or. ratNumGetDenominator(total) /= 2) &
      error stop 'incorrect fraction'
   print *, '1/3 + 1/6 = ', ratNumToStr(total)
   print *, 'PASS rational_number'
end program
