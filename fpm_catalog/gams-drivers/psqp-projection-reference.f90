! Independent API consumer; see licenses/projection-lbfgs-drivers-MIT.txt.
module projection_problem
   use psqp_module, only: psqp_class,wp=>psqp_wp
   implicit none
   real(wp), allocatable :: center(:),target(:)
   real(wp) :: radius,height
   integer :: objective_gradients=0,constraint_gradients=0
contains
   subroutine objective(me,nf,x,f)
      class(psqp_class), intent(inout) :: me
      integer :: nf
      real(wp) :: x(nf),f
      f=0.5_wp*sum((x-center-target)**2)
   end subroutine objective
   subroutine objective_gradient(me,nf,x,g)
      class(psqp_class), intent(inout) :: me
      integer :: nf
      real(wp) :: x(nf),g(nf)
      g=x-center-target
      objective_gradients=objective_gradients+1
   end subroutine objective_gradient
   subroutine constraint(me,nf,kc,x,c)
      class(psqp_class), intent(inout) :: me
      integer :: nf,kc
      real(wp) :: x(nf),c
      select case(kc)
      case(1)
         c=x(1)-center(1)-height
      case(2)
         c=radius**2-sum((x-center)**2)
      case default
         error stop 'constraint index'
      end select
   end subroutine constraint
   subroutine constraint_gradient(me,nf,kc,x,g)
      class(psqp_class), intent(inout) :: me
      integer :: nf,kc
      real(wp) :: x(nf),g(nf)
      select case(kc)
      case(1)
         g=0; g(1)=1
      case(2)
         g=-2*(x-center)
      case default
         error stop 'constraint gradient index'
      end select
      constraint_gradients=constraint_gradients+1
   end subroutine constraint_gradient
end module projection_problem

program checked_projections
   use projection_problem
   use ieee_arithmetic, only: ieee_is_finite
   implicit none
   integer, parameter :: sizes(3)=[2,3,5]
   real(wp), parameter :: radii(2)=[0.5_wp,2.0_wp]
   real(wp), allocatable :: x(:),exact(:),y(:),xl(:),xu(:),stationarity(:)
   integer, allocatable :: ix(:)
   real(wp) :: cf(3),cl(2),cu(2),rpar(5),f,gmax,cmax,free_radius,mu,nu,exact_f,calculated_f
   real(wp) :: solution_error,objective_error,violation,kkt,worst_solution=0,worst_objective=0
   real(wp) :: worst_violation=0,worst_kkt=0
   integer :: ic(2),ipar(6),status,n,s,r,translation,pattern,start,i,cases=0,entries=0
   do s=1,3
      n=sizes(s)
      allocate(center(n),target(n),x(n),exact(n),y(n),xl(n),xu(n),stationarity(n),ix(n))
      do r=1,2
         radius=radii(r); height=0.25_wp*radius; free_radius=sqrt(radius**2-height**2)
         do translation=0,1
            center=[(real(translation,wp)*(0.25_wp*i-0.75_wp),i=1,n)]
            do pattern=1,2
               target(1)=0.7_wp*radius
               do i=2,n
                  target(i)=real(i,wp)
                  if (pattern==2) target(i)=target(i)*(-1.0_wp)**i
               end do
               target(2:)=2*radius*target(2:)/norm2(target(2:))
               exact(1)=height
               exact(2:)=free_radius*target(2:)/norm2(target(2:))
               exact_f=0.5_wp*sum((exact-target)**2)
               mu=(norm2(target(2:))/free_radius-1)/2
               nu=target(1)-(1+2*mu)*height
               do start=1,2
                  block
                     type(psqp_class) :: solver
                     x=center+0.25_wp*target
                     if (start==2) x=center+1.25_wp*target
                     x(1)=center(1)+height
                     ix=0; xl=0; xu=0; ic=[5,1]; cl=0; cu=0
                     ipar=[500,5000,0,0,1,1]
                     rpar=[0.0_wp,1e-10_wp,1e-10_wp,1e-8_wp,0.0_wp]
                     objective_gradients=0; constraint_gradients=0
                     call solver%psqpn(n,0,2,x,ix,xl,xu,cf,ic,cl,cu,ipar,rpar,f,gmax,cmax,0,status, &
                        objective,objective_gradient,constraint,constraint_gradient)
                     if (status<1.or.status>4) then
                        print *, 'Projection status: ',n,r,translation,pattern,start,status
                        error stop 'PSQP convergence status'
                     end if
                     if (.not.all(ieee_is_finite(x)).or..not.all(ieee_is_finite([f,gmax,cmax]))) &
                        error stop 'nonfinite projection'
                     if (objective_gradients<1.or.constraint_gradients<1) error stop 'analytic gradients not called'
                     y=x-center; calculated_f=0.5_wp*sum((y-target)**2)
                     solution_error=maxval(abs(y-exact))/(1+maxval(abs(exact)))
                     objective_error=abs(calculated_f-exact_f)/(1+exact_f)
                     violation=max(abs(y(1)-height)/(1+radius), &
                        max(0.0_wp,sum(y**2)-radius**2)/(1+radius**2))
                     stationarity=(1+2*mu)*y-target; stationarity(1)=stationarity(1)+nu
                     kkt=maxval(abs(stationarity))/(1+norm2(target))
                     worst_solution=max(worst_solution,solution_error); worst_objective=max(worst_objective,objective_error)
                     worst_violation=max(worst_violation,violation); worst_kkt=max(worst_kkt,kkt)
                     if (solution_error>2e-5_wp.or.objective_error>5e-8_wp.or.violation>2e-7_wp.or.kkt>5e-5_wp) &
                        error stop 'analytic projection certificate'
                     if (abs(f-calculated_f)/(1+calculated_f)>5e-8_wp) error stop 'reported objective mismatch'
                     cases=cases+1; entries=entries+n
                  end block
               end do
            end do
         end do
      end do
      deallocate(center,target,x,exact,y,xl,xu,stationarity,ix)
   end do
   print '(a,i0)', 'Ball-and-plane projection problems: ',cases
   print '(a,i0)', 'Analytic optimizer entries: ',entries
   print '(a,es12.4)', 'Maximum normalized optimizer error: ',worst_solution
   print '(a,es12.4)', 'Maximum normalized objective error: ',worst_objective
   print '(a,es12.4)', 'Maximum normalized constraint violation: ',worst_violation
   print '(a,es12.4)', 'Maximum analytic-multiplier stationarity residual: ',worst_kkt
   print '(a)', 'PASS psqp-projection-reference'
end program checked_projections
