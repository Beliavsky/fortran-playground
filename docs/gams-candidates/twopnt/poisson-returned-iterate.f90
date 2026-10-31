! Original I1b API driver. MIT: licenses/boundary-spectral-drivers-MIT.txt.
module poisson_problem
   use twopnt_core, only: TwoPntBVProblem,TwoPntBVPDomain,RK
   implicit none
   type,extends(TwoPntBVProblem) :: poisson
      real(RK),allocatable :: previous(:)
   contains
      procedure :: fun=>residual
      procedure :: save_sol=>save_previous
      procedure :: update_grid=>grid_updated
   end type
contains
   subroutine residual(this,error,text,points,time,stride,x,buffer)
      class(poisson),intent(inout) :: this
      logical,intent(out) :: error
      integer,intent(in) :: text,points
      logical,intent(in) :: time
      real(RK),intent(in) :: stride,x(*)
      real(RK),intent(inout) :: buffer(*)
      real(RK) :: values(points),f(points),left_flux,right_flux
      integer :: i
      error=.false.
      values=buffer(:points)
      f(1)=values(1)
      f(points)=values(points)
      do i=2,points-1
         left_flux=(values(i)-values(i-1))/(x(i)-x(i-1))
         right_flux=(values(i+1)-values(i))/(x(i+1)-x(i))
         f(i)=2*(right_flux-left_flux)/(x(i+1)-x(i-1))+2
         if(time) f(i)=f(i)-(values(i)-this%previous(i))/stride
      end do
      buffer(:points)=f
   end subroutine
   subroutine save_previous(this,vars,buffer)
      class(poisson),intent(inout) :: this
      type(TwoPntBVPDomain),intent(in) :: vars
      real(RK),intent(in) :: buffer(vars%N())
      this%previous=buffer
   end subroutine
   subroutine grid_updated(this,error,vars,u)
      class(poisson),intent(inout) :: this
      logical,intent(out) :: error
      type(TwoPntBVPDomain),intent(in) :: vars
      real(RK),intent(inout) :: u(:)
      error=vars%points/=size(this%previous) ! This example deliberately uses fixed grids.
   end subroutine
end module
program main
   use poisson_problem
   use ieee_arithmetic, only: ieee_is_finite
   implicit none
   integer,parameter :: grids(*)=[9,17,33]
   integer :: c
   do c=1,size(grids)
      call run(grids(c))
   end do
   print '(a)', 'PASS twopnt-poisson-reference'
contains
   subroutine run(n)
      integer,intent(in) :: n
      type(poisson) :: problem
      real(RK) :: values(n),expected(n),h,error_value,error_residual
      logical :: failed
      character(24) :: reason
      call problem%domain%new(failed,0,0,1,n,n,0,[2._RK],[-1._RK],'u',XRANGE=[0._RK,1._RK])
      if(failed) error stop 'Poisson domain initialization'
      problem%setup%adapt=.false.
      problem%setup%leveld=1
      problem%setup%levelm=2
      problem%setup%ssabs=1.e-11_RK
      problem%setup%ssrel=1.e-11_RK
      allocate(problem%previous(n),source=0._RK)
      values=0 ! Deliberately not the known nonzero solution.
      call problem%run(failed,6,reason,values)
      if(failed) error stop 'Poisson BVP solve'
      if(problem%domain%points/=n) error stop 'unexpected adaptive grid'
      if(.not.all(ieee_is_finite(values))) error stop 'nonfinite Poisson solution'
      expected=problem%domain%x(:n)*(1-problem%domain%x(:n))
      error_value=maxval(abs(values-expected))
      h=1._RK/(n-1)
      error_residual=maxval(abs((values(:n-2)-2*values(2:n-1)+values(3:n))/h**2+2))
      if(error_value>1.e-8_RK .or. error_residual>1.e-7_RK) then
         print '(a,i0,a,a,2es16.6)', 'Failed grid ',n,'; reason=',reason,error_value,error_residual
         print '(a,*(1x,f12.7))', 'Returned profile:',values
         print '(a,*(1x,f12.7))', 'Expected profile:',expected
         error stop 'known Poisson profile/residual'
      end if
      if(max(abs(values(1)),abs(values(n)))>1.e-10_RK) error stop 'Poisson boundary conditions'
      print '(a,i0,a,2es14.5)', 'Grid points: ',n,'; profile/residual errors: ',error_value,error_residual
      print '(a,f16.12)', 'Computed midpoint u(0.5): ',values((n+1)/2)
   end subroutine
end program
