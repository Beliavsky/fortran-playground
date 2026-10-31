! Independent API consumer; MIT: licenses/higher-ad-drivers-MIT.txt.
! This short process retains derivative graphs until exit; disposal is not tested.
program main
   use diffstruc
   use ieee_arithmetic,only:ieee_is_finite
   implicit none
   type node_handle
      type(array_type),pointer::p=>null()
   end type node_handle
   type(array_type),target::x(5)
   type(node_handle)::f(5),derivative(6,5)
   real(real32),parameter::points(3,5)=reshape([0.5_real32,-1.0_real32,2.0_real32, &
      -0.75_real32,0.5_real32,1.25_real32,0.0_real32,0.0_real32,0.0_real32, &
      2.0_real32,-0.5_real32,-1.0_real32,1.0_real32,2.0_real32,-2.0_real32],[3,5])
   real(real32)::directions(3,6),v(3),expected_value,gradient(3),hessian(3,3),actual_hessian(3,3)
   real(real32)::forward(6),reverse(3),expected,error,worst
   integer::sample,j,i,checks,forward_calls,reverse_calls
   directions=0
   do j=1,3
      directions(j,j)=1
   end do
   directions(:,4)=[1.0_real32,-2.0_real32,0.5_real32]
   directions(:,5)=[-0.5_real32,0.0_real32,2.0_real32]
   worst=0; checks=0; forward_calls=0; reverse_calls=0
   do sample=1,5
      v=points(:,sample)
      call x(sample)%allocate(array_shape=[3,1])
      x(sample)%is_temporary=.false.
      x(sample)%val(:,1)=v
      call x(sample)%set_requires_grad(.true.)
      f(sample)%p => pack(x(sample),[1],1)**3 + pack(x(sample),[1],1)*pack(x(sample),[2],1) &
         + pack(x(sample),[2],1)*pack(x(sample),[3],1)**2 + pack(x(sample),[3],1)**2
      if (.not.associated(f(sample)%p)) error stop 'expression graph missing'
      f(sample)%p%is_temporary=.false.
      expected_value=v(1)**3+v(1)*v(2)+v(2)*v(3)**2+v(3)**2
      gradient=[3*v(1)**2+v(2),v(1)+v(3)**2,2*(v(2)+1)*v(3)]
      hessian=reshape([6*v(1),1.0_real32,0.0_real32,1.0_real32,0.0_real32,2*v(3), &
                      0.0_real32,2*v(3),2*(v(2)+1)],[3,3])
      call check(f(sample)%p%val(1,1),expected_value)
      do j=1,6
         call x(sample)%set_direction(directions(:,j))
         derivative(j,sample)%p => f(sample)%p%grad_forward(x(sample))
         if (.not.associated(derivative(j,sample)%p)) error stop 'forward graph missing'
         derivative(j,sample)%p%is_temporary=.false.
         forward(j)=derivative(j,sample)%p%val(1,1)
         expected=sum(gradient*directions(:,j))
         call check(forward(j),expected)
         forward_calls=forward_calls+1
      end do
      ! Reverse mode needs the full direction mask restored after directional passes.
      call x(sample)%set_direction([1.0_real32,1.0_real32,1.0_real32])
      call f(sample)%p%grad_reverse(reset_graph=.true.)
      if (.not.associated(x(sample)%grad)) error stop 'reverse gradient missing'
      reverse=x(sample)%grad%val(:,1)
      do i=1,3
         call check(reverse(i),gradient(i))
      end do
      reverse_calls=reverse_calls+1
      do j=1,3
         call derivative(j,sample)%p%grad_reverse(reset_graph=.true.)
         if (.not.associated(x(sample)%grad)) error stop 'Hessian row missing'
         actual_hessian(:,j)=x(sample)%grad%val(:,1)
         do i=1,3
            call check(actual_hessian(i,j),hessian(i,j))
         end do
         reverse_calls=reverse_calls+1
      end do
      if (maxval(abs(actual_hessian-transpose(actual_hessian)))>1e-5_real32) error stop 'Hessian symmetry'
   end do
   if (checks/=95.or.forward_calls/=30.or.reverse_calls/=20) error stop 'fixture accounting'
   print '(a,i0,a,i0)', 'Three-variable polynomial points: 5; forward calls: ',forward_calls,'; reverse calls: ',reverse_calls
   print '(a,i0)', 'Exact values, directional derivatives, gradient and Hessian entries: ',checks
   print '(a,es12.4)', 'Maximum normalized REAL32 reference error: ',worst
   print '(a)', 'PASS diffstruc-hessian-reference'
contains
   subroutine check(actual,reference)
      real(real32),intent(in)::actual,reference
      if (.not.ieee_is_finite(actual)) error stop 'nonfinite AD value'
      error=abs(actual-reference)/max(1.0_real32,abs(reference))
      if (error>1e-5_real32) error stop 'analytical polynomial derivative'
      worst=max(worst,error); checks=checks+1
   end subroutine check
end program main
