! Small one-process CG solve, following the upstream PSBLAS solver examples.
program main
   use psb_base_mod
   use psb_prec_mod
   use psb_linsolve_mod
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   implicit none
   type(psb_ctxt_type) :: context
   type(psb_desc_type) :: descriptor
   type(psb_dspmat_type) :: a
   type(psb_d_vect_type) :: b, x
   type(psb_dprec_type) :: preconditioner
   integer(psb_ipk_) :: info, rank, processes, iterations
   integer(psb_lpk_) :: indices(3)=[1,2,3], rows(7)=[1,1,2,2,2,3,3], columns(7)=[1,2,1,2,3,2,3]
   real(psb_dpk_) :: values(7)=[4,1,1,3,1,1,2], rhs(3)=[6,10,8], zeros(3)=0
   real(psb_dpk_) :: dense(3,3), residual, error_estimate
   real(psb_dpk_), allocatable :: solution(:)
   call psb_init(context)
   call psb_info(context, rank, processes)
   if (rank /= 0 .or. processes /= 1) error stop 'This example expects one process'
   call psb_cdall(context, descriptor, info, vl=indices)
   call check('descriptor allocation')
   call psb_spall(a, descriptor, info, nnz=7_psb_ipk_)
   call check('sparse allocation')
   call psb_geall(b, descriptor, info)
   call check('rhs allocation')
   call psb_geall(x, descriptor, info)
   call check('solution allocation')
   call psb_spins(7_psb_ipk_, rows, columns, values, a, descriptor, info)
   call check('sparse insertion')
   call psb_geins(3_psb_ipk_, indices, rhs, b, descriptor, info)
   call check('rhs insertion')
   call psb_geins(3_psb_ipk_, indices, zeros, x, descriptor, info)
   call check('initial guess')
   call psb_cdasb(descriptor, info)
   call check('descriptor assembly')
   call psb_spasb(a, descriptor, info, afmt='CSR')
   call check('sparse assembly')
   call psb_geasb(b, descriptor, info)
   call check('rhs assembly')
   call psb_geasb(x, descriptor, info)
   call check('solution assembly')
   call preconditioner%init(context, 'DIAG', info)
   call check('preconditioner initialization')
   call preconditioner%build(a, descriptor, info)
   call check('preconditioner build')
   call psb_krylov('CG', a, preconditioner, b, x, 1.0e-12_psb_dpk_, descriptor, info, &
      itmax=30_psb_ipk_, iter=iterations, err=error_estimate)
   call check('conjugate gradient solve')
   solution = x%get_vect()
   if (size(solution) /= 3) error stop 'Unexpected solution size'
   if (.not. all(ieee_is_finite(solution))) error stop 'Nonfinite solution'
   dense = reshape([4,1,0, 1,3,1, 0,1,2], [3,3])
   residual = maxval(abs(matmul(dense,solution)-rhs))
   if (maxval(abs(solution-[1,2,3])) > 1.0e-10_psb_dpk_ .or. residual > 1.0e-10_psb_dpk_) &
      error stop 'Incorrect sparse solution'
   call preconditioner%free(info)
   call check('preconditioner release')
   call psb_gefree(x, descriptor, info)
   call check('solution release')
   call psb_gefree(b, descriptor, info)
   call check('rhs release')
   call psb_spfree(a, descriptor, info)
   call check('sparse release')
   call psb_cdfree(descriptor, info)
   call check('descriptor release')
   call psb_exit(context)
   print '(a,3f12.7)', 'Solution: ', solution
   print '(a,i0)', 'CG iterations: ', iterations
   print '(a,es12.4)', 'Maximum residual: ', residual
   print '(a)', 'PASS psblas'
contains
   subroutine check(stage)
      character(*), intent(in) :: stage
      if (info /= psb_success_) then
         print '(a,a,a,i0)', 'Failure in ', stage, ': ', info
         error stop 'PSBLAS call failed'
      end if
   end subroutine check
end program main
