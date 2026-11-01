! Independent API consumer; see licenses/gradient-swarm-drivers-MIT.txt.
module quadratic_gradient_problem
   use ForTimize, only: pr
   implicit none
   real(pr), allocatable :: h(:,:),center(:)
   integer :: gradient_calls=0
contains
   subroutine objective(x,f,df,data)
      real(pr), intent(in) :: x(:)
      real(pr), intent(out) :: f
      real(pr), optional, intent(out) :: df(:)
      class(*), optional, intent(inout) :: data
      real(pr) :: displacement(size(x)),gradient(size(x))
      integer :: i,j
      displacement=x-center; gradient=0
      do i=1,size(x)
         do j=1,size(x)
            gradient(i)=gradient(i)+h(i,j)*displacement(j)
         end do
      end do
      f=0.5_pr*sum(displacement*gradient)
      if (present(df)) then
         df=gradient; gradient_calls=gradient_calls+1
      end if
   end subroutine objective
end module quadratic_gradient_problem

program checked_fixed_gradient_steps
   use ForTimize, only: GradientDescent,minimize
   use quadratic_gradient_problem
   use ieee_arithmetic, only: ieee_is_finite
   implicit none
   integer, parameter :: sizes(3)=[2,3,5],counts(5)=[1,2,5,25,100],conditions(2)=[1,5]
   real(pr), allocatable :: q(:,:),lambda(:),initial(:),x(:),expected(:),previous(:),coefficients(:)
   real(pr) :: angle,c,s,temp,step,f,endpoint,initial_f,expected_f,previous_f,error,objective_error
   real(pr) :: worst_point=0,worst_return=0,worst_endpoint=0,worst_final_ratio=0
   integer :: shape_id,n,conditioning,basis,step_id,count_id,iterations,start,i,j,k,cases=0,entries=0
   do shape_id=1,3
      n=sizes(shape_id)
      allocate(h(n,n),center(n),q(n,n),lambda(n),initial(n),x(n),expected(n),previous(n),coefficients(n))
      center=[(real(i-2,pr)/4,i=1,n)]
      do conditioning=1,2
         lambda=[(1+real(conditions(conditioning)-1,pr)*(i-1)/(n-1),i=1,n)]
         do basis=1,2
            q=0
            do i=1,n
               q(i,i)=1
            end do
            if (basis==2) then
               do k=1,n-1
                  angle=0.31_pr*(k+1); c=cos(angle); s=sin(angle)
                  do i=1,n
                     temp=q(i,k); q(i,k)=c*temp-s*q(i,k+1); q(i,k+1)=s*temp+c*q(i,k+1)
                  end do
               end do
            end if
            h=0
            do j=1,n
               do i=1,n
                  do k=1,n
                     h(i,j)=h(i,j)+q(i,k)*lambda(k)*q(j,k)
                  end do
               end do
            end do
            h=0.5_pr*(h+transpose(h))
            do step_id=1,2
               step=0.5_pr/maxval(lambda)
               if (step_id==2) step=1.5_pr/maxval(lambda)
               do count_id=1,5
                  iterations=counts(count_id)
                  do start=1,2
                     block
                        type(GradientDescent) :: solver
                        initial=center+[(real(i,pr)/n,i=1,n)]
                        if (start==2) initial=center+[(-(-1.0_pr)**i*(1+real(i,pr)/n),i=1,n)]
                        coefficients=0
                        do k=1,n
                           do i=1,n
                              coefficients(k)=coefficients(k)+q(i,k)*(initial(i)-center(i))
                           end do
                        end do
                        expected=center; previous=center
                        do k=1,n
                           do i=1,n
                              expected(i)=expected(i)+q(i,k)*(1-step*lambda(k))**iterations*coefficients(k)
                              previous(i)=previous(i)+q(i,k)*(1-step*lambda(k))**(iterations-1)*coefficients(k)
                           end do
                        end do
                        initial_f=0.5_pr*sum(lambda*coefficients**2)
                        expected_f=0.5_pr*sum(lambda*((1-step*lambda)**iterations*coefficients)**2)
                        previous_f=0.5_pr*sum(lambda*((1-step*lambda)**(iterations-1)*coefficients)**2)
                        solver%step=step; solver%max_iters=iterations
                        solver%convergence_tolerance=1e-12_pr
                        x=initial; gradient_calls=0
                        call minimize(objective,x,f,solver)
                        if (gradient_calls/=iterations) error stop 'fixed iteration gradient count'
                        if (.not.all(ieee_is_finite(x)).or..not.ieee_is_finite(f)) error stop 'nonfinite gradient result'
                        error=maxval(abs(x-expected))/(1+maxval(abs(initial-center)))
                        worst_point=max(worst_point,error)
                        if (error>2e-12_pr) error stop 'analytic gradient iterate'
                        ! At this pin returned F is evaluated BEFORE the final position update.
                        objective_error=abs(f-previous_f)/(1+initial_f)
                        worst_return=max(worst_return,objective_error)
                        if (objective_error>2e-12_pr) error stop 'preceding-iterate objective'
                        call objective(x,endpoint)
                        objective_error=abs(endpoint-expected_f)/(1+initial_f)
                        worst_endpoint=max(worst_endpoint,objective_error)
                        if (objective_error>2e-12_pr) error stop 'recomputed endpoint objective'
                        if (endpoint>initial_f*(1+2e-12_pr)) error stop 'quadratic cost increased'
                        if (iterations==100) then
                           worst_final_ratio=max(worst_final_ratio,endpoint/initial_f)
                           if (endpoint/initial_f>1e-8_pr) error stop 'long-run quadratic contraction'
                        end if
                        cases=cases+1; entries=entries+n
                        if (cases==1) print '(a,2es14.5)', 'First returned / endpoint objective: ',f,endpoint
                     end block
                  end do
               end do
            end do
         end do
      end do
      deallocate(h,center,q,lambda,initial,x,expected,previous,coefficients)
   end do
   print '(a,i0)', 'Fixed-step quadratic runs: ',cases
   print '(a,i0)', 'Analytic iterate entries: ',entries
   print '(a,es12.4)', 'Maximum normalized iterate discrepancy: ',worst_point
   print '(a,es12.4)', 'Maximum normalized returned-objective discrepancy: ',worst_return
   print '(a,es12.4)', 'Maximum normalized endpoint-objective discrepancy: ',worst_endpoint
   print '(a,es12.4)', 'Maximum final / initial cost after 100 steps: ',worst_final_ratio
   print '(a)', 'Returned objective is for the preceding iterate; endpoint objective is recomputed.'
   print '(a)', 'PASS fortimize-gradient-reference'
end program checked_fixed_gradient_steps
