! Independent API consumer; see licenses/projection-lbfgs-drivers-MIT.txt.
program checked_lbfgs_quadratics
   use seiscope_optimization_toolbox
   use iso_fortran_env, only: real64
   use ieee_arithmetic, only: ieee_is_finite
   implicit none
   integer, parameter :: sizes(3)=[2,3,5],conditions(3)=[1,5,25]
   real(real64), parameter :: scales(2)=[0.25_real64,2.0_real64]
   real, allocatable :: h(:,:),center(:),x(:),gradient(:)
   real(real64), allocatable :: q(:,:),diagonal(:),h_reference(:,:),delta(:),true_gradient(:)
   real :: cost
   real(real64) :: angle,c,s,temp,initial_cost,true_cost,norm_h,solution_error,objective_error,gradient_error
   real(real64) :: worst_solution=0,worst_objective=0,worst_gradient=0,worst_callback=0,callback_error
   integer :: shape_id,n,conditioning,basis,scale_id,start,i,j,k,flag,calls,cases=0,entries=0
   do shape_id=1,3
      n=sizes(shape_id)
      allocate(h(n,n),center(n),x(n),gradient(n),q(n,n),diagonal(n),h_reference(n,n),delta(n),true_gradient(n))
      do conditioning=1,3
         do basis=1,2
            center=0
            if (basis==2) center=[(real(i-2)/4,i=1,n)]
            q=0
            do i=1,n
               q(i,i)=1
               diagonal(i)=1+real(conditions(conditioning)-1,real64)*(i-1)/(n-1)
            end do
            if (basis==2) then
               do k=1,n-1
                  angle=0.23_real64*(k+1); c=cos(angle); s=sin(angle)
                  do i=1,n
                     temp=q(i,k)
                     q(i,k)=c*temp-s*q(i,k+1); q(i,k+1)=s*temp+c*q(i,k+1)
                  end do
               end do
            end if
            do scale_id=1,2
               h_reference=0
               do j=1,n
                  do i=1,n
                     do k=1,n
                        h_reference(i,j)=h_reference(i,j)+scales(scale_id)*q(i,k)*diagonal(k)*q(j,k)
                     end do
                  end do
               end do
               h=real(h_reference)
               h=0.5*(h+transpose(h))
               h_reference=real(h,real64)
               norm_h=maxval(sum(abs(h_reference),dim=2))
               do start=1,3
                  block
                     type(optim_type) :: solver
                     do i=1,n
                        select case(start)
                        case(1)
                           x(i)=center(i)+real(i)/n
                        case(2)
                           x(i)=center(i)-(-1.0)**i*(1+real(i)/n)
                        case(3)
                           x(i)=center(i)+0.5*cos(real(i))
                        end select
                     end do
                     call evaluate()
                     initial_cost=real(cost,real64)
                     call set_inputs(solver,cost,1000,conv=1e-12,l=10,print_flag=0)
                     flag=0; calls=0
                     do while (flag/=2.and.flag/=4)
                        calls=calls+1
                        if (calls>20000) error stop 'LBFGS request limit'
                        call LBFGS(n,x,cost,gradient,solver,flag)
                        if (flag==1) call evaluate()
                        if (flag<1.or.flag>4) error stop 'unexpected LBFGS request'
                     end do
                     if (flag/=2.or..not.all(ieee_is_finite(x))) then
                        print *, 'LBFGS fixture status: ',n,conditioning,basis,scale_id,start,flag
                        error stop 'LBFGS convergence status'
                     end if
                     call evaluate()
                     delta=real(x,real64)-real(center,real64); true_gradient=0
                     do i=1,n
                        do j=1,n
                           true_gradient(i)=true_gradient(i)+h_reference(i,j)*delta(j)
                        end do
                     end do
                     true_cost=0
                     do i=1,n
                        true_cost=true_cost+0.5_real64*delta(i)*true_gradient(i)
                     end do
                     solution_error=maxval(abs(delta))/(1+maxval(abs(real(center,real64))))
                     objective_error=abs(true_cost)/(1+initial_cost)
                     gradient_error=maxval(abs(true_gradient))/(1+norm_h)
                     worst_solution=max(worst_solution,solution_error); worst_objective=max(worst_objective,objective_error)
                     worst_gradient=max(worst_gradient,gradient_error)
                     if (solution_error>2e-3_real64.or.objective_error>2e-7_real64.or.gradient_error>2e-4_real64) &
                        error stop 'known quadratic optimizer'
                     callback_error=max(abs(real(cost,real64)-true_cost)/(1+abs(true_cost)), &
                        maxval(abs(real(gradient,real64)-true_gradient))/(1+norm_h*maxval(abs(delta))))
                     worst_callback=max(worst_callback,callback_error)
                     if (callback_error>64*epsilon(1.0)) error stop 'independent callback audit'
                     cases=cases+1; entries=entries+n
                  end block
               end do
            end do
         end do
      end do
      deallocate(h,center,x,gradient,q,diagonal,h_reference,delta,true_gradient)
   end do
   print '(a,i0)', 'SPD quadratic minimizations: ',cases
   print '(a,i0)', 'Known minimizer entries: ',entries
   print '(a,es12.4)', 'Maximum normalized minimizer error: ',worst_solution
   print '(a,es12.4)', 'Maximum initial-cost-scaled objective: ',worst_objective
   print '(a,es12.4)', 'Maximum Hessian-scaled gradient: ',worst_gradient
   print '(a,es12.4)', 'Maximum independent real64 callback discrepancy: ',worst_callback
   print '(a)', 'PASS seiscope-lbfgs-reference'
contains
   subroutine evaluate()
      integer :: i,j
      real :: displacement(n)
      displacement=x-center; gradient=0
      do i=1,n
         do j=1,n
            gradient(i)=gradient(i)+h(i,j)*displacement(j)
         end do
      end do
      cost=0.5*sum(displacement*gradient)
      if (.not.ieee_is_finite(cost).or..not.all(ieee_is_finite(gradient))) error stop 'nonfinite callback'
   end subroutine evaluate
end program checked_lbfgs_quadratics
