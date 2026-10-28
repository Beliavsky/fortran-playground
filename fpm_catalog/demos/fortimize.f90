module quadratic_model
   use ForTimize, only: pr
   implicit none
contains
   subroutine objective(x,f,df,data)
      real(pr), intent(in) :: x(:)
      real(pr), intent(out) :: f
      real(pr), optional, intent(out) :: df(:)
      class(*), optional, intent(inout) :: data
      f=(x(1)-2._pr)**2+3._pr*(x(2)+1._pr)**2
      if (present(df)) df=[2*(x(1)-2._pr),6*(x(2)+1._pr)]
   end subroutine
end module
program main
   use ForTimize, only: minimize,NelderMead
   use quadratic_model
   use ieee_arithmetic, only: ieee_is_finite
   implicit none
   type(NelderMead) :: solver
   real(pr) :: x(2),f
   solver%convergence_tolerance=1e-12_pr
   solver%konvge=20
   solver%max_iters=1000
   x=[-3._pr,4._pr]
   call minimize(objective,x,f,solver)
   if (.not.all(ieee_is_finite(x))) error stop
   if (maxval(abs(x-[2._pr,-1._pr]))>1e-4_pr.or.f>1e-8_pr) error stop
   print '(a,2f14.8)', 'Computed minimum at:',x
   print '(a,es13.5)', 'Objective:',f
   print *, 'PASS fortimize'
end program
