! Differentiate exp(x) at zero using an uneven, one-dimensional stencil.
program demo_finite_difference
   use dq_coeff_mod, only: calc_dq_coeff
   use data_types_mod, only: real_kind
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   implicit none
   real(real_kind) :: nodes(3,3), target(3), coeff(3,2), values(3), estimates(2)
   integer :: status
   nodes = 0
   nodes(:,1) = [-0.001_real_kind,0._real_kind,0.002_real_kind]
   target = 0
   call calc_dq_coeff(target,nodes,['d_dx  ','d2_dx2'],coeff,status, &
      set_epsilon2=1e-10_real_kind,taylor_series=0)
   if (status/=0) error stop 'Weight generation failed'
   if (.not. all(ieee_is_finite(coeff))) error stop 'Nonfinite weights'
   values = exp(nodes(:,1))
   estimates = matmul(values,coeff)
   print '(a,2f20.12)', 'First and second derivative: ',estimates
   print '(a,2es14.4)', 'Errors against exact value 1: ',abs(estimates-1)
   if (maxval(abs(estimates-1))>1e-3_real_kind) error stop 'Differentiation failed'
   print '(a)', 'PASS finite_difference'
end program
