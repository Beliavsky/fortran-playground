program constrained_quadratic
   use conmin_module, only: conmin_class, wp => conmin_wp
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   implicit none
   integer, parameter :: n1=4, n2=5, n3=5, n4=5, n5=10
   type(conmin_class) :: solver
   real(wp) :: x(n1), lower(n1), upper(n1), g(n2), scal(n1), df(n1), a(n1,n3)
   real(wp) :: s(n1), g1(n2), g2(n2), b(n3,n3), c(n4), value
   integer :: isc(n2), ic(n3), ms1(n5), i
   ! Minimize x**2+y**2 subject to x+y >= 1. Exact optimum: (0.5,0.5).
   x=1; lower=-10; upper=10; scal=1
   g=0; df=0; a=0; s=0; g1=0; g2=0; b=0; c=0; isc=0; ic=0; ms1=0
   solver%ndv=2; solver%ncon=1; solver%nside=1
   solver%infog=0; solver%info=0; solver%nfdg=0; solver%iprint=0
   solver%itmax=100; solver%icndir=0; solver%nscal=0; solver%itrm=3
   solver%ct=-1.e-6_wp; solver%ctmin=1.e-7_wp
   solver%delfun=1.e-10_wp; solver%dabfun=1.e-10_wp
   solver%igoto=0
   do i=1,1000
      call solver%solve(x,lower,upper,g,scal,df,a,s,g1,g2,b,c,isc,ic,ms1,n1,n2,n3,n4,n5)
      solver%obj=sum(x(1:2)**2)
      g(1)=1-x(1)-x(2)
      if (solver%igoto==0) exit
   end do
   value=sum(x(1:2)**2)
   print '(a,2f12.6)', 'Constrained minimum at: ', x(1:2)
   print '(a,f12.6)', 'Objective (expected 0.5): ', value
   print '(a,es12.4)', 'Constraint violation: ', max(0.0_wp,g(1))
   if (solver%igoto/=0) error stop 'Iteration limit'
   if (.not. all(ieee_is_finite(x(1:2)))) error stop 'Nonfinite result'
   if (maxval(abs(x(1:2)-0.5_wp))>1.e-3_wp .or. g(1)>1.e-4_wp) error stop 'Optimum check'
   print *, 'PASS conmin'
end program
