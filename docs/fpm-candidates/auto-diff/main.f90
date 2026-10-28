program main
   use auto_diff, only: tree_t,rk,assignment(=),operator(+),operator(*),exp
   implicit none
   type(tree_t) :: a,b,c,y
   real(rk) :: gradient(3)
   a=2._rk; b=1._rk; c=0._rk
   y=(a+b*b)*exp(c)
   call y%backward()
   gradient=[a%get_grad(),b%get_grad(),c%get_grad()]
   if (abs(y%get_value()-3._rk)>1e-12_rk) error stop
   print *, 'Computed gradient:',gradient
   if (maxval(abs(gradient-[1._rk,2._rk,3._rk]))>1e-12_rk) error stop
   print '(a,f9.4)', 'y = (a + b*b)*exp(c):',y%get_value()
   print '(a,3f9.4)', 'Gradient with respect to a,b,c:',gradient
   print *, 'PASS auto-diff'
end program main
