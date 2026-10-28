program main
   use iso_fortran_env, only: real64
   use rndgen_mod, only: rndgen
   implicit none
   type(rndgen) :: first,second
   real(real64) :: a(5),b(5),replayed(5)
   integer :: i
   call first%init(12345)
   call second%init(67890)
   do i=1,5
      a(i)=first%rnd(); b(i)=second%rnd()
   end do
   call first%reset()
   do i=1,5
      replayed(i)=first%rnd()
   end do
   if (any(a<0).or.any(a>=1).or.any(b<0).or.any(b>=1)) error stop
   if (any(a/=replayed).or.all(a==b)) error stop 'Seed reproducibility failed'
   print '(a,5f11.7)', 'Seed 12345:',a
   print '(a,5f11.7)', 'Seed 67890:',b
   print *, 'Reset reproduces the first sequence.'
   print *, 'PASS rndgen-fortran'
end program main
