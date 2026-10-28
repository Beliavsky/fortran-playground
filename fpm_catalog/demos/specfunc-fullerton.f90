program main
   use fullerton_gamma, only: fgamma,reciprocal_gamma,digamma
   implicit none
   real :: x,g,rg,psi_difference
   integer :: i
   print '(a)', '      x       Gamma(x)      1/Gamma(x)'
   do i=1,4
      x=real(i)+.5
      g=fgamma(x); rg=reciprocal_gamma(x)
      if (abs(g-gamma(x))>2e-5*max(1.,abs(g)).or.abs(g*rg-1.)>2e-5) error stop
      psi_difference=digamma(x+1.)-digamma(x)
      if (abs(psi_difference-1./x)>2e-5) error stop 'Digamma recurrence failed'
      print '(f8.2,2f16.7)', x,g,rg
   end do
   print *, 'PASS specfunc-fullerton'
end program main
