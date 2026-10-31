! Independent API consumer; MIT: licenses/rkf-qags-drivers-MIT.txt.
module integrands
   use iso_c_binding,only:c_int,c_double,c_ptr,c_f_pointer
   implicit none
   type,bind(c)::settings
      integer(c_int)::family
      real(c_double)::parameter
   end type settings
   integer::evaluations=0
contains
   function integrand(x,params) bind(c) result(y)
      real(c_double),value::x
      type(c_ptr),value::params
      real(c_double)::y,p
      type(settings),pointer::s
      call c_f_pointer(params,s)
      evaluations=evaluations+1; p=s%parameter
      select case(s%family)
      case(1)
         y=x**p
      case(2)
         y=x**p*log(x)
      case(3)
         y=1/(1+(p*x)**2)
      case(4)
         y=exp(p*x)
      case(5)
         y=sin(p*x)
      end select
   end function integrand
end module integrands
program main
   use fgsl
   use integrands
   use iso_c_binding,only:c_loc
   use ieee_arithmetic,only:ieee_is_finite
   implicit none
   integer(fgsl_size_t),parameter::limit=1000
   real(fgsl_double),parameter::powers(*)=[-0.5_fgsl_double,-0.25_fgsl_double,0.5_fgsl_double, &
      2.0_fgsl_double,5.0_fgsl_double]
   type(settings),target::parameters
   type(fgsl_function)::function
   type(fgsl_integration_workspace)::workspace
   real(fgsl_double)::a,b,p,tolerance,reference,value,estimate,error,budget,worst,worst_estimate,pi
   integer(fgsl_int)::status
   integer::family_id,case_id,tolerance_id,ncases,calls,total_evaluations
   calls=0; total_evaluations=0; worst=0; worst_estimate=0; pi=acos(-1.0_fgsl_double)
   function=fgsl_function_init(integrand,c_loc(parameters))
   workspace=fgsl_integration_workspace_alloc(limit)
   if (.not.fgsl_well_defined(workspace)) error stop 'workspace allocation'
   do tolerance_id=1,2
      tolerance=1e-7_fgsl_double
      if (tolerance_id==2) tolerance=1e-10_fgsl_double
      do family_id=1,5
         ncases=3
         if (family_id<=2) ncases=5
         if (family_id==5) ncases=4
         do case_id=1,ncases
            parameters%family=family_id
            select case(family_id)
            case(1,2)
               p=powers(case_id); a=0; b=1
               reference=1/(p+1)
               if (family_id==2) reference=-1/(p+1)**2
            case(3)
               p=real(case_id,fgsl_double)/2
               if (case_id==3) p=2
               a=-2; b=3
               reference=(atan(p*b)-atan(p*a))/p
            case(4)
               p=-1
               if (case_id==2) p=0.5_fgsl_double
               if (case_id==3) p=2
               a=-1; b=2
               reference=(exp(p*b)-exp(p*a))/p
            case(5)
               p=real(2*case_id-1,fgsl_double)
               if (case_id==4) p=16
               a=0; b=pi
               reference=(1-cos(p*pi))/p
            end select
            parameters%parameter=p; evaluations=0
            status=fgsl_integration_qags(function,a,b,tolerance,tolerance,limit,workspace,value,estimate)
            if (status/=fgsl_success) then
               print '(a,4i5)', 'Family/case/tolerance/status: ',family_id,case_id,tolerance_id,status
               error stop 'QAGS status'
            end if
            if (.not.ieee_is_finite(value).or..not.ieee_is_finite(estimate)) error stop 'nonfinite quadrature'
            if (evaluations<=0) error stop 'integrand not called'
            error=abs(value-reference)/max(1.0_fgsl_double,abs(reference))
            if (error>5*tolerance) error stop 'analytical integral'
            budget=max(tolerance,tolerance*abs(value))
            if (estimate<0.or.estimate>budget+32*epsilon(value)*max(1.0_fgsl_double,abs(value))) &
               error stop 'error estimate outside requested budget'
            worst=max(worst,error)
            worst_estimate=max(worst_estimate,estimate/max(1.0_fgsl_double,abs(reference)))
            total_evaluations=total_evaluations+evaluations; calls=calls+1
         end do
      end do
      print '(a,es12.4,a)', 'Requested absolute/relative tolerance ',tolerance,': all five integral families passed.'
   end do
   call fgsl_function_free(function)
   call fgsl_integration_workspace_free(workspace)
   if (calls/=40) error stop 'fixture accounting'
   print '(a,i0)', 'Adaptive finite-interval integrals with one reused workspace: ',calls
   print '(a,i0)', 'Integrand evaluations: ',total_evaluations
   print '(a,es12.4)', 'Maximum normalized analytical integral error: ',worst
   print '(a,es12.4)', 'Maximum normalized reported error estimate: ',worst_estimate
   print '(a)', 'PASS fgsl-qags-reference'
end program main
