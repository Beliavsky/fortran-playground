! Independent MIT consumer; see licenses/next-numerical-drivers-MIT.txt.
module numerical_objective
   use iso_fortran_env,only:wp=>real64
   implicit none
   logical::rosenbrock
   real(wp)::center(5)
   integer::calls
contains
   function objective(x,args) result(value)
      real(wp),intent(in)::x(:)
      class(*),optional,intent(inout)::args
      real(wp)::value,d(size(x))
      integer::i
      calls=calls+1
      if(rosenbrock) then
         value=(1-x(1))**2+100*(x(2)-x(1)**2)**2
      else
         d=x-center(:size(x))
         value=sum([(real(i,wp)*d(i)**2,i=1,size(x))])+sum(d)**2/4
      end if
   end function
end module
program main
   use numerical_objective
   use nonlin,only:bfgs,fcnnvar_helper,fcnnvar,iteration_behavior
   use ieee_arithmetic,only:ieee_is_finite
   implicit none
   real(wp),allocatable::x(:),delta(:),gradient(:)
   real(wp)::reported,value,error,worst_x,worst_g
   integer::n,variant,i,fits
   worst_x=0;worst_g=0;fits=0
   do n=2,5
      do variant=1,3
         allocate(x(n),delta(n),gradient(n))
         center(:n)=[(real(i-3,wp)/4,i=1,n)]
         x=center(:n)+real(2*variant-4,wp)/2+0.25_wp
         rosenbrock=.false.
         call solve()
         deallocate(x,delta,gradient)
      end do
   end do
   allocate(x(2),delta(2),gradient(2));rosenbrock=.true.
   do variant=1,3
      select case(variant)
      case(1)
         x=[-1.2_wp,1._wp]
      case(2)
         x=[0._wp,0._wp]
      case(3)
         x=[1.5_wp,2._wp]
      end select
      call solve()
   end do
   print '(a,i0)', 'Finite-difference BFGS fits with no gradient callback: ',fits
   print '(a,2es14.5)', 'Worst normalized parameter / independent gradient errors: ',worst_x,worst_g
   print '(a)', 'PASS nonlin-bfgs-finite-differences-reference'
contains
   subroutine solve()
      type(bfgs)::solver
      type(fcnnvar_helper)::helper
      type(iteration_behavior)::tracking
      procedure(fcnnvar),pointer::callback
      real(wp)::scale
      callback=>objective
      call helper%set_fcn(callback,size(x))
      ! Intentionally no set_gradient_fcn: the package must difference the objective.
      call solver%set_max_fcn_evals(10000)
      call solver%set_tolerance(1.e-10_wp)
      calls=0
      call solver%solve(helper,x,reported,tracking)
      if(.not.(tracking%converge_on_fcn.or.tracking%converge_on_chng.or.tracking%converge_on_zero_diff)) &
         error stop 'BFGS stopping status'
      if(calls<=0.or..not.all(ieee_is_finite(x)).or..not.ieee_is_finite(reported)) error stop 'Finite result'
      if(rosenbrock) then
         delta=x-1;scale=1
         value=(1-x(1))**2+100*(x(2)-x(1)**2)**2
         gradient=[2*(x(1)-1)-400*x(1)*(x(2)-x(1)**2),200*(x(2)-x(1)**2)]
      else
         delta=x-center(:size(x));scale=max(1._wp,maxval(abs(center(:size(x)))))
         value=sum([(real(i,wp)*delta(i)**2,i=1,size(x))])+sum(delta)**2/4
         gradient=[(2*i*delta(i)+sum(delta)/2,i=1,size(x))]
      end if
      error=maxval(abs(delta))/scale
      if(error>5.e-5_wp.or.value>2.e-9_wp.or.maxval(abs(gradient))>2.e-5_wp) then
         print *, 'Rosenbrock / size / final:',rosenbrock,size(x),x
         print *, 'Parameter / objective / gradient:',error,value,maxval(abs(gradient))
         error stop 'Known minimum and stationarity'
      end if
      if(abs(reported-value)>1.e-12_wp) error stop 'Reported objective'
      worst_x=max(worst_x,error);worst_g=max(worst_g,maxval(abs(gradient)));fits=fits+1
   end subroutine
end program
