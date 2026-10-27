program main
   use lbfgsb_module, only: setulb, wp => lbfgsp_wp
   implicit none
   integer, parameter :: n=2, m=5
   real(wp) :: x(n), lower(n), upper(n), f, g(n), wa(2*m*n+5*n+11*m*m+8*m), dsave(29)
   integer :: bounds(n), iwa(3*n), isave(44), iteration
   logical :: lsave(4)
   character(60) :: task, csave
   x = 0.0_wp
   lower = -1.0_wp
   upper = 1.0_wp
   bounds = 2
   task = 'START'
   ! The unconstrained minimum is (2,2); the bounded minimum is (1,1).
   do iteration = 1, 100
      call setulb(n,m,x,lower,upper,bounds,f,g,1.e7_wp,1.e-8_wp, &
         wa,iwa,task,-1,csave,lsave,isave,dsave)
      if (task(1:2) == 'FG') then
         f = sum((x-2.0_wp)**2)
         g = 2*(x-2.0_wp)
      else if (task(1:5) /= 'NEW_X') then
         exit
      end if
   end do
   if (task(1:4) /= 'CONV' .or. maxval(abs(x-1.0_wp)) > 1.e-8_wp) error stop 'incorrect optimum'
   print *, 'Bounded minimum at:', x
   print *, 'PASS lbfgsb'
end program
