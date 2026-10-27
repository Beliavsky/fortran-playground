program main
   use specfun_module, only: bernob, wp => specfun_wp
   implicit none
   real(wp) :: bernoulli(0:6)
   call bernob(6,bernoulli)
   if (abs(bernoulli(2)-1.0_wp/6) > 1.e-12_wp) error stop 'incorrect B2'
   if (abs(bernoulli(4)+1.0_wp/30) > 1.e-12_wp) error stop 'incorrect B4'
   if (abs(bernoulli(6)-1.0_wp/42) > 1.e-12_wp) error stop 'incorrect B6'
   print *, 'Even Bernoulli numbers B0 to B6:', bernoulli(0:6:2)
   print *, 'PASS specfun'
end program
